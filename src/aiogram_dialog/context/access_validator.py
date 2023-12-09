from logging import getLogger

from aiogram.enums import ChatType
from aiogram.types import Chat, User

from aiogram_dialog.api.entities import (
    Stack,
)

logger = getLogger(__name__)


class DefaultAccessValidator:
    async def is_allowed(
            self, stack: Stack, user: User, chat: Chat,
    ) -> bool:
        if not stack.access_settings:
            return True
        if chat.type is ChatType.PRIVATE:
            return True
        if stack.access_settings.user_ids:
            if user.id not in stack.access_settings.user_ids:
                return False
        return True
