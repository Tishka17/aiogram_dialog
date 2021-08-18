import warnings
from logging import getLogger
from typing import Optional, Type, Dict, Union, Any, Callable, Awaitable

from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.dispatcher.filters.base import BaseFilter
from aiogram.dispatcher.fsm.state import StatesGroup, State

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.dispatcher.fsm.storage.base import BaseStorage
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, Update

from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.types.base import TelegramObject

from .context import Context
from .events import DialogUpdateEvent
from .storage import StorageProxy
from ..exceptions import InvalidStackIdError
from ..utils import remove_indent_id, get_chat

STORAGE_KEY = "aiogd_storage_proxy"
STACK_KEY = "aiogd_stack"
CONTEXT_KEY = "aiogd_context"
CALLBACK_DATA_KEY = "aiogd_original_callback_data"

logger = getLogger(__name__)


class IntentFilter(BaseFilter):
    aiogd_intent_state_group: Optional[Type[StatesGroup]]

    async def __call__(
            self, message: Update, aiogd_stack, aiogd_context, **kwargs
    ) -> bool:
        if self.aiogd_intent_state_group is None:
            return True
        context: Context = aiogd_context
        if not context:
            return False
        return context and context.state.group == self.aiogd_intent_state_group


class IntentMiddleware(BaseMiddleware):
    def __init__(self, storage: BaseStorage, state_groups: Dict[str, Type[StatesGroup]]):
        super().__init__()
        self.storage = storage
        self.state_groups = state_groups

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        # ToDo AiodgUpdate

        if isinstance(event, DialogUpdateEvent):
            await self.on_pre_process_aiogd_update(event, data)
        elif event.message:
            await self.on_pre_process_message(event.message, data)
        elif event.chat_member:
            await self.on_pre_process_message(event.message, data)
        elif event.callback_query:
            await self.on_pre_process_callback_query(event.callback_query, data)

        result = await handler(event, data)

        await self.on_post_process_message(data)

        return result

    async def on_pre_process_message(self, event: Union[Message, ChatMemberUpdated], data: dict):
        chat = get_chat(event)
        proxy = StorageProxy(
            bot=data.get('bot'),
            storage=self.storage,
            user_id=event.from_user.id,
            chat_id=chat.id,
            state_groups=self.state_groups,
        )
        stack = await proxy.load_stack()
        if stack.empty():
            context = None
        else:
            context = await proxy.load_context(stack.last_intent_id())
        data[STORAGE_KEY] = proxy
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context

    async def on_post_process_message(self, data: dict):
        proxy: StorageProxy = data.pop(STORAGE_KEY)
        await proxy.save_context(data.pop(CONTEXT_KEY))
        await proxy.save_stack(data.pop(STACK_KEY))

    async def on_pre_process_aiogd_update(self, event: DialogUpdateEvent, data: dict):
        chat = get_chat(event)
        proxy = StorageProxy(
            bot=data.get('bot'),
            storage=self.storage,
            user_id=event.from_user.id,
            chat_id=chat.id,
            state_groups=self.state_groups,
        )
        data[STORAGE_KEY] = proxy
        if event.intent_id is not None:
            context = await proxy.load_context(event.intent_id)
            stack = await proxy.load_stack(context.stack_id)
        elif event.stack_id is not None:
            stack = await proxy.load_stack(event.stack_id)
            if stack.empty():
                if event.intent_id is not None:
                    logger.warning(f"Outdated intent id ({event.intent_id}) "
                                   f"for empty stack ({stack.id})")
                    raise CancelHandler()
                context = None
            else:
                if event.intent_id is not None and event.intent_id != stack.last_intent_id():
                    logger.warning(f"Outdated intent id ({event.intent_id}) "
                                   f"for stack ({stack.id})")
                    raise CancelHandler()
                context = await proxy.load_context(stack.last_intent_id())
        else:
            raise InvalidStackIdError(f"Both stack id and intent id are None: {event}")

        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context

    async def on_pre_process_callback_query(self, event: CallbackQuery, data: dict):
        chat = get_chat(event)
        proxy = StorageProxy(
            bot=data.get('bot'),
            storage=self.storage,
            user_id=event.from_user.id,
            chat_id=chat.id,
            state_groups=self.state_groups,
        )
        data[STORAGE_KEY] = proxy

        original_data = event.data
        print(event.data)
        intent_id, callback_data = remove_indent_id(event.data)
        if intent_id:
            context = await proxy.load_context(intent_id)
            stack = await proxy.load_stack(context.stack_id)
            if stack.last_intent_id() != intent_id:
                logger.warning(f"Outdated intent id ({intent_id}) for stack ({stack.id})")
                raise CancelHandler()
            event.Config.allow_mutation = True  # ToDo
            event.data = callback_data
            event.Config.allow_mutation = False
        else:
            context = None
            stack = await proxy.load_stack()
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context
        data[CALLBACK_DATA_KEY] = original_data