from logging import getLogger

from aiogram.enums import ChatType

from aiogram_dialog import ChatEvent
from aiogram_dialog.api.entities import (
    Stack,
)
from aiogram_dialog.api.protocols import StackAccessValidator

logger = getLogger(__name__)


class DefaultAccessValidator(StackAccessValidator):
    async def is_allowed(
            self, stack: Stack, event: ChatEvent, data: dict,
    ) -> bool:
        if not stack.access_settings:
            return True
        chat = data["event_chat"]
        if chat.type is ChatType.PRIVATE:
            return True
        if stack.access_settings.user_ids:
            user = data["event_from_user"]
            if user.id not in stack.access_settings.user_ids:
                return False
        return True
