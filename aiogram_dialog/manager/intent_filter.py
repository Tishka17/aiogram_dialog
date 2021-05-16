import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from aiogram.types.base import TelegramObject


class IntentFilter(BoundFilter):
    key = 'intent_state_group'

    def __init__(self, intent_state_group: typing.Optional[bool] = None):
        self.intent_state_group = intent_state_group

    async def check(self, obj: TelegramObject):
        if self.intent_state_group is None:
            return True
        data = ctx_data.get()
        return data.get("intent_state_group") == self.intent_state_group
