from logging import getLogger
from typing import Any, Awaitable, Callable, Dict, Optional, cast

from aiogram import Router
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Chat, Message, TelegramObject, User
from aiogram.types.error_event import ErrorEvent

from aiogram_dialog.api.entities import (DEFAULT_STACK_ID, ChatEvent, Context,
                                         DialogUpdateEvent, Stack)
from aiogram_dialog.api.exceptions import (InvalidStackIdError, OutdatedIntent,
                                           UnknownIntent, UnknownState)
from aiogram_dialog.api.internal import (CALLBACK_DATA_KEY, CONTEXT_KEY,
                                         EVENT_SIMULATED, STACK_KEY,
                                         STORAGE_KEY, ReplyCallbackQuery)
from aiogram_dialog.api.protocols import DialogRegistryProtocol
from aiogram_dialog.utils import remove_intent_id, split_reply_callback

from .storage import StorageProxy

logger = getLogger(__name__)


class IntentMiddlewareFactory:
    def __init__(
        self,
        registry: DialogRegistryProtocol,
    ):
        super().__init__()
        self.registry = registry

    def storage_proxy(self, data: Dict[str, Any]) -> StorageProxy:
        return StorageProxy(
            bot=data["bot"],
            storage=data["fsm_storage"],
            user_id=data["event_from_user"].id,
            chat_id=data["event_chat"].id,
            state_groups=self.registry.states_groups(),
        )

    def _check_outdated(self, intent_id: str, stack: Stack) -> None:
        """Check if intent id is outdated for stack."""
        if stack.empty():
            raise OutdatedIntent(
                stack.id,
                f"Outdated intent id ({intent_id}) " f"for stack ({stack.id})",
            )
        elif intent_id != stack.last_intent_id():
            raise OutdatedIntent(
                stack.id,
                f"Outdated intent id ({intent_id}) " f"for stack ({stack.id})",
            )

    async def _load_context(
        self,
        event: ChatEvent,
        intent_id: Optional[str],
        stack_id: Optional[str],
        data: Dict[str, Any],
    ) -> None:
        proxy = self.storage_proxy(data)
        logger.debug(
            "Loading context for intent: `%s`, " "stack: `%s`, user: `%s`, chat: `%s`",
            intent_id,
            stack_id,
            cast(User, event.from_user).id,
            proxy.chat_id,
        )
        if intent_id is not None:
            context = await proxy.load_context(intent_id)
            stack = await proxy.load_stack(context.stack_id)
            self._check_outdated(intent_id, stack)
        elif stack_id is not None:
            stack = await proxy.load_stack(stack_id)
            if stack.empty():
                context = None
            else:
                context = await proxy.load_context(stack.last_intent_id())
        else:
            raise InvalidStackIdError(
                f"Both stack id and intent id are None: {event}",
            )
        data[STORAGE_KEY] = proxy
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context

    def _intent_id_from_reply(
        self,
        event: Message,
        data: Dict[str, Any],
    ) -> Optional[str]:
        if not (
            event.reply_to_message
            and cast(User, event.reply_to_message.from_user).id == data["bot"].id
            and event.reply_to_message.reply_markup
            and event.reply_to_message.reply_markup.inline_keyboard
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
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        text, callback_data = split_reply_callback(event.text)
        if callback_data:
            query = ReplyCallbackQuery(
                id="",
                message=None,
                original_message=event,
                data=callback_data,
                from_user=event.from_user,  # type: ignore[call-arg]
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
            await self._load_context(event, intent_id, DEFAULT_STACK_ID, data)
        else:
            await self._load_context(event, None, DEFAULT_STACK_ID, data)
        return await handler(event, data)

    async def process_my_chat_member(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        await self._load_context(event, None, DEFAULT_STACK_ID, data)
        return await handler(event, data)

    async def process_chat_join_request(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        await self._load_context(event, None, DEFAULT_STACK_ID, data)
        return await handler(event, data)

    async def process_aiogd_update(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: DialogUpdateEvent,
        data: Dict[str, Any],
    ) -> Any:
        await self._load_context(event, event.intent_id, event.stack_id, data)
        return await handler(event, data)

    async def process_callback_query(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if "event_chat" not in data:
            return await handler(event, data)
        proxy = self.storage_proxy(data)
        data[STORAGE_KEY] = proxy

        original_data = event.data
        if event.data:
            intent_id, callback_data = remove_intent_id(event.data)
            await self._load_context(event, intent_id, DEFAULT_STACK_ID, data)
            data[CALLBACK_DATA_KEY] = original_data
        else:
            await self._load_context(event, None, DEFAULT_STACK_ID, data)
        return await handler(event, data)


SUPPORTED_ERROR_EVENTS = {
    "message",
    "callback_query",
    "my_chat_member",
    "aiogd_update",
}


async def context_saver_middleware(
    handler: Callable[
        [TelegramObject, Dict[str, Any]],
        Awaitable[Any],
    ],
    event: TelegramObject,
    data: Dict[str, Any],
) -> Any:
    result = await handler(event, data)
    proxy: StorageProxy = data.pop(STORAGE_KEY, None)
    if proxy:
        await proxy.save_context(data.pop(CONTEXT_KEY))
        await proxy.save_stack(data.pop(STACK_KEY))
    return result


class IntentErrorMiddleware(BaseMiddleware):
    def __init__(
        self,
        registry: DialogRegistryProtocol,
    ):
        super().__init__()
        self.registry = registry

    def _is_error_supported(
        self,
        event: ErrorEvent,
        data: Dict[str, Any],
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
        self,
        storage: StorageProxy,
        stack: Stack,
    ) -> None:
        while not stack.empty():
            await storage.remove_context(stack.pop())
        await storage.save_stack(stack)

    async def _load_last_context(
        self,
        storage: StorageProxy,
        stack: Stack,
        chat: Chat,
        user: User,
    ) -> Optional[Context]:
        try:
            return await storage.load_context(stack.last_intent_id())
        except (UnknownIntent, OutdatedIntent):
            logger.warning(
                "Stack is broken for user %s, chat %s, resetting",
                user.id,
                chat.id,
            )
            await self._fix_broken_stack(storage, stack)
        return None

    async def __call__(
        self,
        handler: Callable[
            [ErrorEvent, Dict[str, Any]],
            Awaitable[Any],
        ],
        event: ErrorEvent,  # type: ignore[override]
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
                user_id=user.id,
                chat_id=chat.id,
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
                    storage=proxy,
                    stack=stack,
                    chat=chat,
                    user=user,
                )
            data[STACK_KEY] = stack
            data[CONTEXT_KEY] = context
            return await handler(event, data)
        finally:
            storage_proxy: StorageProxy = data.pop(STORAGE_KEY, None)
            if storage_proxy:
                context = data.pop(CONTEXT_KEY)
                if context is not None:
                    await storage_proxy.save_context(context)
                await storage_proxy.save_stack(data.pop(STACK_KEY))
