import typing
from logging import getLogger

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.dispatcher.handler import ctx_data, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.storage import BaseStorage
from aiogram.types import Message, CallbackQuery
from aiogram.types.base import TelegramObject

from storage import StorageProxy
from .intent import Intent
from ..utils import remove_indent_id

STORAGE_KEY = "aiogd_storage_proxy"
STACK_KEY = "aiogd_stack"
INTENT_KEY = "aiogd_intent"
CALLBACK_DATA_KEY = "aiogd_original_callback_data"

logger = getLogger(__name__)


class IntentFilter(BoundFilter):
    key = 'diodg_intent_state_group'

    def __init__(self, diodg_intent_state_group: typing.Optional[bool] = None):
        self.intent_state_group = diodg_intent_state_group

    async def check(self, obj: TelegramObject):
        if self.intent_state_group is None:
            return True
        data = ctx_data.get()
        intent: Intent = data.get(INTENT_KEY)
        return intent and intent.state.group == self.intent_state_group


class IntentMiddleware(BaseMiddleware):
    def __init__(self, storage: BaseStorage,
                 state_groups: typing.Dict[str, typing.Type[StatesGroup]]):
        super().__init__()
        self.storage = storage
        self.state_groups = state_groups

    async def on_pre_process_message(self, event: Message, data: dict):
        proxy = StorageProxy(
            storage=self.storage,
            user_id=event.from_user.id,
            chat_id=event.chat.id,
            state_groups=self.state_groups,
        )
        stack = await proxy.load_stack()
        if stack.empty():
            intent = None
        else:
            intent = await proxy.load_intent(stack.last_intent_id())
        data[STORAGE_KEY] = proxy
        data[STACK_KEY] = stack
        data[INTENT_KEY] = intent

    async def on_post_process_message(self, _, result, data: dict):
        proxy: StorageProxy = data.pop(STORAGE_KEY)
        await proxy.save_intent(data.pop(INTENT_KEY))
        await proxy.save_stack(data.pop(STACK_KEY))

    async def on_pre_process_callback_query(self, event: CallbackQuery, data: dict):
        proxy = StorageProxy(
            storage=self.storage,
            user_id=event.from_user.id,
            chat_id=event.message.chat.id,
            state_groups=self.state_groups,
        )
        data[STORAGE_KEY] = proxy

        original_data = event.data
        intent_id, callback_data = remove_indent_id(event.data)
        if not intent_id:
            return
        event.data = callback_data
        intent = await proxy.load_intent(intent_id)
        stack = await proxy.load_stack(intent.stack_id)
        if stack.last_intent_id() != intent_id:
            logger.warning(f"Outdated intent id ({intent_id}) for stack ({stack.id})")
            raise CancelHandler()
        data[STACK_KEY] = stack
        data[INTENT_KEY] = intent
        data[CALLBACK_DATA_KEY] = original_data

    on_post_process_callback_query = on_post_process_message
