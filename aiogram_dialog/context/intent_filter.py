from logging import getLogger
from typing import Optional, Type, Dict, Any

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.storage import BaseStorage
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, Update
from aiogram.types.base import TelegramObject

from .context import Context
from .events import DialogUpdateEvent, ChatEvent
from .stack import DEFAULT_STACK_ID
from .storage import StorageProxy
from ..exceptions import InvalidStackIdError, OutdatedIntent
from ..utils import remove_indent_id, get_chat

STORAGE_KEY = "aiogd_storage_proxy"
STACK_KEY = "aiogd_stack"
CONTEXT_KEY = "aiogd_context"
CALLBACK_DATA_KEY = "aiogd_original_callback_data"

logger = getLogger(__name__)


class IntentFilter(BoundFilter):
    key = 'aiogd_intent_state_group'

    def __init__(
            self,
            aiogd_intent_state_group: Optional[Type[StatesGroup]] = None
    ):
        self.intent_state_group = aiogd_intent_state_group

    async def check(self, obj: TelegramObject):
        if self.intent_state_group is None:
            return True
        data = ctx_data.get()
        context: Context = data.get(CONTEXT_KEY)
        if not context:
            return False
        return context and context.state.group == self.intent_state_group


class IntentMiddleware(BaseMiddleware):
    def __init__(
            self, storage: BaseStorage,
            state_groups: Dict[str, Type[StatesGroup]]
    ) -> None:
        super().__init__()
        self.storage = storage
        self.state_groups = state_groups

    async def _load_context(
            self, event: ChatEvent,
            intent_id: Optional[str], stack_id: Optional[str],
            data: dict,
    ) -> None:
        chat = get_chat(event)
        proxy = StorageProxy(
            storage=self.storage,
            user_id=event.from_user.id,
            chat_id=chat.id,
            state_groups=self.state_groups,
        )
        logger.debug(
            "Loading context for intent: `%s`, "
            "stack: `%s`, user: `%s`, chat: `%s`",
            intent_id, stack_id, event.from_user.id, chat.id,
        )
        if intent_id is not None:
            context = await proxy.load_context(intent_id)
            stack = await proxy.load_stack(context.stack_id)
        elif stack_id is not None:
            stack = await proxy.load_stack(stack_id)
            if stack.empty():
                if intent_id is not None:
                    raise OutdatedIntent(
                        stack.id,
                        f"Outdated intent id ({intent_id}) "
                        f"for stack ({stack.id})",
                    )
                context = None
            else:
                if intent_id is not None and intent_id != stack.last_intent_id():
                    raise OutdatedIntent(
                        stack.id,
                        f"Outdated intent id ({intent_id}) "
                        f"for stack ({stack.id})",
                    )
                context = await proxy.load_context(stack.last_intent_id())
        else:
            raise InvalidStackIdError(
                f"Both stack id and intent id are None: {event}",
            )
        data[STORAGE_KEY] = proxy
        data[STACK_KEY] = stack
        data[CONTEXT_KEY] = context

    async def on_pre_process_message(
            self, event: Message, data: dict,
    ) -> None:
        if (
                event.reply_to_message and
                event.reply_to_message.from_user.id == event.bot.id and
                event.reply_to_message.reply_markup and
                event.reply_to_message.reply_markup.inline_keyboard
        ):
            button = event.reply_to_message.reply_markup.inline_keyboard[0][0]
            intent_id, callback_data = remove_indent_id(button.callback_data)
            await self._load_context(
                event, intent_id, DEFAULT_STACK_ID, data,
            )
        else:
            await self._load_context(
                event, None, DEFAULT_STACK_ID, data,
            )

    async def on_post_process_message(
            self, message: Message, result, data: dict,
    ) -> None:
        proxy: StorageProxy = data.pop(STORAGE_KEY)
        await proxy.save_context(data.pop(CONTEXT_KEY))
        await proxy.save_stack(data.pop(STACK_KEY))

    async def on_pre_process_aiogd_update(
            self, event: DialogUpdateEvent, data: dict
    ) -> None:
        await self._load_context(
            event, event.intent_id, event.stack_id, data,
        )

    async def on_pre_process_callback_query(self, event: CallbackQuery,
                                            data: dict):
        original_data = event.data
        intent_id, callback_data = remove_indent_id(event.data)
        await self._load_context(
            event, intent_id, None, data,
        )
        logger.debug("Original callback data: %s", original_data)
        event.data = callback_data
        data[CALLBACK_DATA_KEY] = original_data

    async def on_pre_process_my_chat_member(
            self,
            event: ChatMemberUpdated,
            data: dict
    ) -> None:
        await self._load_context(
            event, None, DEFAULT_STACK_ID, data,
        )

    on_post_process_callback_query = on_post_process_message
    on_post_process_aiogd_update = on_post_process_message
    on_post_process_my_chat_member = on_post_process_message

    async def on_pre_process_error(
            self, update: Update, error: Exception, data: dict,
    ) -> None:
        if isinstance(error, InvalidStackIdError):
            return

        event = (
                update.message or
                update.my_chat_member or
                update.callback_query
        )
        if not event:
            return

        chat = get_chat(event)

        proxy = StorageProxy(
            storage=self.storage,
            user_id=event.from_user.id,
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

    async def on_post_process_error(
            self, event: Any, error: Exception, result: list, data: dict,
    ) -> None:
        proxy: StorageProxy = data.pop(STORAGE_KEY, None)
        if not proxy:
            return
        context = data.pop(CONTEXT_KEY)
        if context is not None:
            await proxy.save_context(context)
        await proxy.save_stack(data.pop(STACK_KEY))
