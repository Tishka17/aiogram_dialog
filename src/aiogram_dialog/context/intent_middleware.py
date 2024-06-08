from logging import getLogger
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import Router
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.fsm.storage.base import BaseEventIsolation
from aiogram.types import CallbackQuery, Chat, Message, User
from aiogram.types.error_event import ErrorEvent

from aiogram_dialog.api.entities import (
    ChatEvent, Context, DEFAULT_STACK_ID, DialogUpdateEvent, Stack,
)
from aiogram_dialog.api.exceptions import (
    InvalidStackIdError, OutdatedIntent, UnknownIntent, UnknownState,
)
from aiogram_dialog.api.internal import (
    CALLBACK_DATA_KEY, CONTEXT_KEY, EVENT_SIMULATED,
    ReplyCallbackQuery, STACK_KEY, STORAGE_KEY,
)
from aiogram_dialog.api.protocols import (
    DialogRegistryProtocol, StackAccessValidator,
)
from aiogram_dialog.utils import remove_intent_id, split_reply_callback
from .storage import StorageProxy

logger = getLogger(__name__)


class IntentMiddlewareFactory:
    def __init__(
            self,
            registry: DialogRegistryProtocol,
            access_validator: StackAccessValidator,
            events_isolation: BaseEventIsolation,
    ):
        super().__init__()
        self.registry = registry
        self.access_validator = access_validator
        self.events_isolation = events_isolation

    def storage_proxy(self, data: dict):
        proxy = StorageProxy(
            bot=data["bot"],
            storage=data["fsm_storage"],
            events_isolation=self.events_isolation,
            state_groups=self.registry.states_groups(),
            user_id=data["event_from_user"].id,
            chat_id=data["event_chat"].id,
            thread_id=data.get("event_thread_id"),
        )
        return proxy

    def _check_outdated(self, intent_id: str, stack: Stack):
        """Check if intent id is outdated for stack."""
        if stack.empty():
            raise OutdatedIntent(
                stack.id,
                f"Outdated intent id ({intent_id}) "
                f"for stack ({stack.id})",
            )
        elif intent_id != stack.last_intent_id():
            raise OutdatedIntent(
                stack.id,
                f"Outdated intent id ({intent_id}) "
                f"for stack ({stack.id})",
            )

    async def _load_stack(
            self,
            event: ChatEvent,
            stack_id: Optional[str],
            proxy: StorageProxy,
            data: dict,
    ) -> Optional[Stack]:
        if stack_id is None:
            raise InvalidStackIdError("Both stack id and intent id are None")
        stack = await proxy.load_stack(stack_id)
        if not await self.access_validator.is_allowed(stack, event, data):
            user = data["event_from_user"]
            logger.debug(
                "Stack %s is not allowed for user %s",
                stack.id, user.id,
            )
            await proxy.unlock()
            return
        return stack

    async def _load_context_by_stack(
            self,
            event: ChatEvent,
            proxy: StorageProxy,
            stack_id: Optional[str],
            data: dict,
    ) -> None:
        user = data["event_from_user"]
        chat = data["event_chat"]
        logger.debug(
            "Loading context for stack: `%s`, user: `%s`, chat: `%s`",
            stack_id, user.id, chat.id,
        )
        stack = await self._load_stack(event, stack_id, proxy, data)
        if not stack:
            return
        if stack.empty():
            context = None
        else:
            try:
                context = await proxy.load_context(stack.last_intent_id())
            except:
                await proxy.unlock()
                raise
        data[STORAGE_KEY] = proxy
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context

    async def _load_context_by_intent(
            self,
            event: ChatEvent,
            proxy: StorageProxy,
            intent_id: Optional[str],
            data: dict,
    ) -> None:
        user = data["event_from_user"]
        chat = data["event_chat"]
        logger.debug(
            "Loading context for intent: `%s`, user: `%s`, chat: `%s`",
            intent_id, user.id, chat.id,
        )
        context = await proxy.load_context(intent_id)
        stack = await self._load_stack(event, context.stack_id, proxy, data)
        if not stack:
            return
        try:
            self._check_outdated(intent_id, stack)
        except:
            await proxy.unlock()
            raise

        data[STORAGE_KEY] = proxy
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context

    async def _load_default_context(
            self, event: ChatEvent, data: dict,
    ) -> None:
        return await self._load_context_by_stack(
            event=event,
            proxy=self.storage_proxy(data),
            stack_id=DEFAULT_STACK_ID,
            data=data,
        )

    def _intent_id_from_reply(
            self, event: Message, data: dict,
    ) -> Optional[str]:
        if not (
                event.reply_to_message and
                event.reply_to_message.from_user.id == data["bot"].id and
                event.reply_to_message.reply_markup and
                event.reply_to_message.reply_markup.inline_keyboard
        ):
            return None
        for row in event.reply_to_message.reply_markup.inline_keyboard:
            for button in row:
                if button.callback_data:
                    intent_id, _ = remove_intent_id(button.callback_data)
                    return intent_id
        return None

    async def process_message(
            self,
            handler: Callable,
            event: Message,
            data: dict,
    ):
        text, callback_data = split_reply_callback(event.text)
        if callback_data:
            query = ReplyCallbackQuery(
                id="",
                message=None,
                original_message=event,
                data=callback_data,
                from_user=event.from_user,
                # we cannot know real chat instance
                chat_instance=str(event.chat.id),
            ).as_(data["bot"])
            router: Router = data["event_router"]
            return await router.propagate_event(
                "callback_query",
                query,
                **{EVENT_SIMULATED: True},
                **data,
            )

        if intent_id := self._intent_id_from_reply(event, data):
            await self._load_context_by_intent(
                event=event,
                proxy=self.storage_proxy(data),
                intent_id=intent_id,
                data=data,
            )
        else:
            await self._load_default_context(event, data)
        return await handler(event, data)

    async def process_my_chat_member(
            self,
            handler: Callable,
            event: Message,
            data: dict,
    ) -> None:
        await self._load_default_context(event, data)
        return await handler(event, data)

    async def process_chat_join_request(
            self,
            handler: Callable,
            event: Message,
            data: dict,
    ) -> None:
        await self._load_default_context(event, data)
        return await handler(event, data)

    async def process_aiogd_update(
            self,
            handler: Callable,
            event: DialogUpdateEvent,
            data: dict,
    ):
        if event.intent_id:
            await self._load_context_by_intent(
                event=event,
                proxy=self.storage_proxy(data),
                intent_id=event.intent_id,
                data=data,
            )
        else:
            await self._load_context_by_stack(
                event=event,
                proxy=self.storage_proxy(data),
                stack_id=event.stack_id,
                data=data,
            )
        return await handler(event, data)

    async def process_callback_query(
            self,
            handler: Callable,
            event: CallbackQuery,
            data: dict,
    ):
        if "event_chat" not in data:
            return await handler(event, data)
        original_data = event.data
        if event.data:
            intent_id, callback_data = remove_intent_id(event.data)
            if intent_id:
                await self._load_context_by_intent(
                    event=event,
                    proxy=self.storage_proxy(data),
                    intent_id=intent_id,
                    data=data,
                )
            else:
                await self._load_default_context(event, data)
            data[CALLBACK_DATA_KEY] = original_data
        else:
            await self._load_default_context(event, data)
        return await handler(event, data)


SUPPORTED_ERROR_EVENTS = {
    "message",
    "callback_query",
    "my_chat_member",
    "aiogd_update",
}


async def context_saver_middleware(handler, event, data):
    result = await handler(event, data)
    proxy: StorageProxy = data.pop(STORAGE_KEY, None)
    if proxy:
        await proxy.save_context(data.pop(CONTEXT_KEY))
        await proxy.save_stack(data.pop(STACK_KEY))
    return result


async def context_unlocker_middleware(handler, event, data):
    proxy: StorageProxy = data.get(STORAGE_KEY, None)
    try:
        result = await handler(event, data)
    finally:
        if proxy:
            await proxy.unlock()
    return result


class IntentErrorMiddleware(BaseMiddleware):
    def __init__(
            self,
            registry: DialogRegistryProtocol,
            events_isolation: BaseEventIsolation,
    ):
        super().__init__()
        self.registry = registry
        self.events_isolation = events_isolation

    def _is_error_supported(
            self, event: ErrorEvent, data: Dict[str, Any],
    ) -> bool:
        if isinstance(event, InvalidStackIdError):
            return False
        if event.update.event_type not in SUPPORTED_ERROR_EVENTS:
            return False
        if "event_chat" not in data:
            return False
        if "event_from_user" not in data:
            return False
        return True

    async def _fix_broken_stack(
            self, storage: StorageProxy, stack: Stack,
    ) -> None:
        while not stack.empty():
            await storage.remove_context(stack.pop())
        await storage.save_stack(stack)

    async def _load_last_context(
            self, storage: StorageProxy, stack: Stack,
            chat: Chat, user: User,
    ) -> Optional[Context]:
        try:
            return await storage.load_context(stack.last_intent_id())
        except (UnknownIntent, OutdatedIntent):
            logger.warning(
                "Stack is broken for user %s, chat %s, resetting",
                user.id, chat.id,
            )
            await self._fix_broken_stack(storage, stack)
        return None

    async def __call__(
            self,
            handler: Callable[
                [ErrorEvent, Dict[str, Any]], Awaitable[Any],
            ],
            event: ErrorEvent,
            data: Dict[str, Any],
    ) -> Any:
        error = event.exception
        if not self._is_error_supported(event, data):
            return await handler(event, data)

        try:
            chat = data["event_chat"]
            user = data["event_from_user"]

            proxy = StorageProxy(
                bot=data["bot"],
                storage=data["fsm_storage"],
                events_isolation=self.events_isolation,
                user_id=user.id,
                chat_id=chat.id,
                thread_id=data.get("event_thread_id"),
                state_groups=self.registry.states_groups(),
            )
            data[STORAGE_KEY] = proxy
            if isinstance(error, OutdatedIntent):
                stack = await proxy.load_stack(stack_id=error.stack_id)
            else:
                stack = await proxy.load_stack()
            if stack.empty() or isinstance(error, UnknownState):
                context = None
            else:
                context = await self._load_last_context(
                    storage=proxy, stack=stack, chat=chat, user=user,
                )
            data[STACK_KEY] = stack
            data[CONTEXT_KEY] = context
            return await handler(event, data)
        finally:
            proxy: StorageProxy = data.pop(STORAGE_KEY, None)
            if proxy:
                await proxy.unlock()
                context = data.pop(CONTEXT_KEY)
                if context is not None:
                    await proxy.save_context(context)
                await proxy.save_stack(data.pop(STACK_KEY))
