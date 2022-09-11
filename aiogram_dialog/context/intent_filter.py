from typing import Optional, Type

from aiogram.filters import BaseFilter
from aiogram.fsm.state import StatesGroup
from aiogram.types import TelegramObject

from aiogram_dialog.api.entities import Context
from aiogram_dialog.api.internal import CONTEXT_KEY


class IntentFilter(BaseFilter):
    aiogd_intent_state_group: Optional[Type[StatesGroup]]

    async def __call__(self, obj: TelegramObject, **kwargs) -> bool:
        del obj  # unused
        if self.aiogd_intent_state_group is None:
            return True

        context: Context = kwargs[CONTEXT_KEY]
        if not context:
            return False
        return context.state.group == self.aiogd_intent_state_group
