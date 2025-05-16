import logging
from contextlib import AsyncExitStack
from copy import copy
from typing import Optional

from aiogram import Bot
from aiogram.enums import ChatType, ContentType
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage, StorageKey
from aiogram.types import Chat

from aiogram_dialog.api.entities import (
    DEFAULT_STACK_ID,
    AccessSettings,
    Context,
    OldMessage,
    Stack,
)
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState

logger = logging.getLogger(__name__)


class StorageProxy:
    def __init__(
        self,
        storage: BaseStorage,
        events_isolation: BaseEventIsolation,
        user_id: Optional[int],
        chat_id: int,
        thread_id: Optional[int],
        business_connection_id: Optional[str],
        bot: Bot,
        state_groups: dict[str, type[StatesGroup]],
    ):
        self.storage = storage
        self.events_isolation = events_isolation
        self.state_groups = state_groups
        self.user_id = user_id
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.business_connection_id = business_connection_id
        self.bot = bot
        self.lock_stack = AsyncExitStack()

    async def lock(self, key: StorageKey):
        await self.lock_stack.enter_async_context(
            self.events_isolation.lock(key),
        )

    async def unlock(self):
        await self.lock_stack.aclose()

    async def load_context(self, intent_id: str) -> Context:
        data = await self.storage.get_data(
            key=self._context_key(intent_id),
        )
        if not data:
            raise UnknownIntent(
                f"Context not found for intent id: {intent_id}",
            )
        data["access_settings"] = self._parse_access_settings(
            data.pop("access_settings", None),
        )
        data["state"] = self._state(data["state"])
        return Context(**data)

    def _default_access_settings(self, stack_id: str) -> AccessSettings:
        if stack_id == DEFAULT_STACK_ID and self.user_id:
            return AccessSettings(user_ids=[self.user_id])
        else:
            return AccessSettings(user_ids=[])

    async def load_stack(self, stack_id: str = DEFAULT_STACK_ID) -> Stack:
        fixed_stack_id = self._fixed_stack_id(stack_id)
        key = self._stack_key(fixed_stack_id)
        await self.lock(key)
        data = await self.storage.get_data(key)

        access_settings_data = data.pop("access_settings", None)
        access_settings = self._default_access_settings(stack_id)
        if access_settings_data:
            access_settings = (
                self._parse_access_settings(access_settings_data) or access_settings
            )

        if not data:
            return Stack(_id=fixed_stack_id, access_settings=access_settings)

        loaded_sent_messages = []
        if data.get("sent_messages"):
            for msg_data in data["sent_messages"]:
                chat_type_enum_val = msg_data.get("chat_type")
                chat_type_obj = (
                    ChatType(chat_type_enum_val) if chat_type_enum_val else None
                )
                chat_obj = Chat(id=msg_data["chat_id"], type=chat_type_obj)

                content_type_enum_val = msg_data.get("content_type")
                content_type_obj = (
                    ContentType(content_type_enum_val)
                    if content_type_enum_val
                    else None
                )
                loaded_sent_messages.append(
                    OldMessage(
                        message_id=msg_data["message_id"],
                        chat=chat_obj,
                        has_reply_keyboard=msg_data["has_reply_keyboard"],
                        text=msg_data.get("text"),
                        media_uniq_id=msg_data.get("media_uniq_id"),
                        media_id=msg_data.get("media_id"),
                        business_connection_id=msg_data.get("business_connection_id"),
                        content_type=content_type_obj,
                    ),
                )
        data["sent_messages"] = loaded_sent_messages

        valid_stack_fields = {f_name for f_name in Stack.__dataclass_fields__.keys()}
        filtered_data = {k: v for k, v in data.items() if k in valid_stack_fields}

        return Stack(access_settings=access_settings, **filtered_data)

    async def save_context(self, context: Optional[Context]) -> None:
        if not context:
            return
        data = copy(vars(context))
        data["state"] = data["state"].state
        data["access_settings"] = self._dump_access_settings(
            context.access_settings,
        )
        await self.storage.set_data(
            key=self._context_key(context.id),
            data=data,
        )

    async def remove_context(self, intent_id: str):
        await self.storage.set_data(
            key=self._context_key(intent_id),
            data={},
        )

    async def remove_stack(self, stack_id: str):
        await self.storage.set_data(
            key=self._stack_key(stack_id),
            data={},
        )

    async def save_stack(self, stack: Optional[Stack]) -> None:
        if not stack:
            return
        if stack.empty() and not stack.sent_messages:
            await self.storage.set_data(
                key=self._stack_key(stack.id),
                data={},
            )
        else:
            serializable_sent_messages = []
            for om in stack.sent_messages:
                chat_type_to_save = None
                if om.chat.type:
                    if isinstance(om.chat.type, ChatType):
                        chat_type_to_save = om.chat.type.value
                    elif isinstance(om.chat.type, str):
                        chat_type_to_save = om.chat.type
                    else:
                        logger.warning(
                            f"Unexpected type for chat.type: {type(om.chat.type)}",
                        )
                        chat_type_to_save = str(om.chat.type)

                content_type_to_save = None
                if om.content_type:
                    if isinstance(om.content_type, ContentType):
                        content_type_to_save = om.content_type.value
                    elif isinstance(om.content_type, str):
                        content_type_to_save = om.content_type
                    else:
                        logger.warning(
                            f"Unexpected type for content_type: {type(om.content_type)}",
                        )
                        content_type_to_save = str(om.content_type)

                serializable_sent_messages.append(
                    {
                        "message_id": om.message_id,
                        "chat_id": om.chat.id,
                        "chat_type": chat_type_to_save,
                        "has_reply_keyboard": om.has_reply_keyboard,
                        "text": om.text,
                        "media_uniq_id": om.media_uniq_id,
                        "media_id": om.media_id,
                        "business_connection_id": om.business_connection_id,
                        "content_type": content_type_to_save,
                    },
                )

            data_to_save = {
                "_id": stack.id,
                "intents": stack.intents,
                "sent_messages": serializable_sent_messages,
                "last_income_media_group_id": stack.last_income_media_group_id,
            }
            await self.storage.set_data(
                key=self._stack_key(stack.id),
                data=data_to_save,
            )

    def _context_key(self, intent_id: str) -> StorageKey:
        return StorageKey(
            bot_id=self.bot.id,
            chat_id=self.chat_id,
            user_id=self.chat_id,
            thread_id=self.thread_id,
            business_connection_id=self.business_connection_id,
            destiny=f"aiogd:context:{intent_id}",
        )

    def _fixed_stack_id(self, stack_id: str) -> str:
        if stack_id != DEFAULT_STACK_ID:
            return stack_id
        # private chat has chat_id=user_id and no business connection
        if self.user_id in (None, self.chat_id) and self.business_connection_id is None:
            return stack_id
        return f"<{self.user_id}>"

    def _stack_key(self, stack_id: str) -> StorageKey:
        stack_id = self._fixed_stack_id(stack_id)
        return StorageKey(
            bot_id=self.bot.id,
            chat_id=self.chat_id,
            user_id=self.chat_id,
            thread_id=self.thread_id,
            business_connection_id=self.business_connection_id,
            destiny=f"aiogd:stack:{stack_id}",
        )

    def _state(self, state: str) -> State:
        group, *_ = state.partition(":")
        try:
            for real_state in self.state_groups[group].__all_states__:
                if real_state.state == state:
                    return real_state
        except KeyError:
            raise UnknownState(f"Unknown state group {group}") from None
        raise UnknownState(f"Unknown state {state}")

    def _parse_access_settings(
        self,
        raw: Optional[dict],
    ) -> Optional[AccessSettings]:
        if not raw:
            return None
        return AccessSettings(
            user_ids=raw.get("user_ids") or [],
            custom=raw.get("custom"),
        )

    def _dump_access_settings(
        self,
        access_settings: Optional[AccessSettings],
    ) -> Optional[dict]:
        if not access_settings:
            return None
        return {
            "user_ids": access_settings.user_ids,
            "custom": access_settings.custom,
        }
