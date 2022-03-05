from logging import getLogger
from typing import Optional, Type, Dict, Union, Any, Callable, Awaitable

from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.dispatcher.filters.base import BaseFilter
from aiogram.dispatcher.fsm.state import StatesGroup
from aiogram.dispatcher.fsm.storage.base import BaseStorage
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import (
    Message, CallbackQuery, Update, TelegramObject, ChatMemberUpdated,
)

from .context import Context
from .events import DialogUpdateEvent, DialogUpdate
from .storage import StorageProxy
from ..exceptions import InvalidStackIdError, OutdatedIntent
from ..utils import remove_indent_id

STORAGE_KEY = "aiogd_storage_proxy"
STACK_KEY = "aiogd_stack"
CONTEXT_KEY = "aiogd_context"
CALLBACK_DATA_KEY = "aiogd_original_callback_data"

logger = getLogger(__name__)


class IntentFilter(BaseFilter):
    aiogd_intent_state_group: Optional[Type[StatesGroup]]

    async def __call__(
            self, obj: TelegramObject, **kwargs
    ) -> bool:
        if self.aiogd_intent_state_group is None:
            return True

        context: Context = kwargs[CONTEXT_KEY]
        if not context:
            return False
        return context and context.state.group == self.aiogd_intent_state_group


class IntentMiddlewareFactory:
    def __init__(self, storage: BaseStorage,
                 state_groups: Dict[str, Type[StatesGroup]]):
        super().__init__()
        self.storage = storage
        self.state_groups = state_groups

    def storage_proxy(self, data: dict):
        proxy = StorageProxy(
            bot=data['bot'],
            storage=self.storage,
            user_id=data['event_from_user'].id,
            chat_id=data['event_chat'].id,
            state_groups=self.state_groups,
        )
        return proxy

    async def process_message(
            self, handler: Callable, event: Message, data: dict,
    ):
        proxy = self.storage_proxy(data)
        stack = await proxy.load_stack()
        if stack.empty():
            context = None
        else:
            context = await proxy.load_context(stack.last_intent_id())
        data[STORAGE_KEY] = proxy
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context
        return await handler(event, data)

    process_my_chat_member = process_message

    async def process_aiogd_update(
            self, handler: Callable, event: DialogUpdateEvent, data: dict,
    ):
        proxy = self.storage_proxy(data)
        data[STORAGE_KEY] = proxy
        if event.intent_id is not None:
            context = await proxy.load_context(event.intent_id)
            stack = await proxy.load_stack(context.stack_id)
        elif event.stack_id is not None:
            stack = await proxy.load_stack(event.stack_id)
            if stack.empty():
                if event.intent_id is not None:
                    raise OutdatedIntent(
                        stack.id,
                        f"Outdated intent id ({event.intent_id}) "
                        f"for stack ({stack.id})"
                    )
                context = None
            else:
                if event.intent_id is not None and event.intent_id != stack.last_intent_id():
                    raise OutdatedIntent(
                        stack.id,
                        f"Outdated intent id ({event.intent_id}) "
                        f"for stack ({stack.id})"
                    )
                context = await proxy.load_context(stack.last_intent_id())
        else:
            raise InvalidStackIdError(
                f"Both stack id and intent id are None: {event}"
            )

        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context
        return await handler(event, data)

    async def process_callback_query(
            self, handler: Callable, event: CallbackQuery, data: dict,
    ):
        proxy = self.storage_proxy(data)
        data[STORAGE_KEY] = proxy

        original_data = event.data
        intent_id, callback_data = remove_indent_id(event.data)
        if intent_id:
            context = await proxy.load_context(intent_id)
            stack = await proxy.load_stack(context.stack_id)
            if stack.last_intent_id() != intent_id:
                raise OutdatedIntent(
                    stack.id,
                    f"Outdated intent id ({intent_id}) for stack ({stack.id})"
                )
        else:
            stack = await proxy.load_stack()
            if stack.empty():
                context = None
            else:
                context = await proxy.load_context(stack.last_intent_id())
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context
        data[CALLBACK_DATA_KEY] = original_data
        return await handler(event, data)


SUPPORTED_ERROR_EVENTS = {'message', 'callback_query', 'my_chat_member'}


async def context_saver_middleware(handler, event, data):
    result = await handler(event, data)
    proxy: StorageProxy = data.pop(STORAGE_KEY, None)
    if proxy:
        await proxy.save_context(data.pop(CONTEXT_KEY))
        await proxy.save_stack(data.pop(STACK_KEY))
    return result


class IntentErrorMiddleware(BaseMiddleware):
    def __init__(self, storage: BaseStorage,
                 state_groups: Dict[str, Type[StatesGroup]]):
        super().__init__()
        self.storage = storage
        self.state_groups = state_groups

    async def __call__(
            self,
            handler: Callable[
                [Union[Update, DialogUpdate], Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:

        try:
            error = data["exception"]
            if isinstance(error, InvalidStackIdError):
                return
            if event.event_type not in SUPPORTED_ERROR_EVENTS:
                return

            chat = data['event_chat']

            proxy = StorageProxy(
                bot=data['bot'],
                storage=self.storage,
                user_id=data['event_from_user'].id,
                chat_id=chat.id,
                state_groups=self.state_groups,
            )
            data[STORAGE_KEY] = proxy

            if isinstance(error, OutdatedIntent):
                stack = await proxy.load_stack(stack_id=error.stack_id)
            else:
                stack = await proxy.load_stack()
            if stack.empty():
                context = None
            else:
                context = await proxy.load_context(stack.last_intent_id())
            data[STACK_KEY] = stack
            data[CONTEXT_KEY] = context

            return await handler(event, data)
        finally:
            proxy: StorageProxy = data.pop(STORAGE_KEY, None)
            if not proxy:
                return
            context = data.pop(CONTEXT_KEY)
            if context is not None:
                await proxy.save_context(context)
            await proxy.save_stack(data.pop(STACK_KEY))
