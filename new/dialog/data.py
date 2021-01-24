from typing import Any

from aiogram.dispatcher.storage import FSMContextProxy, FSMContext

GLOBAL_CONTEXT = "__AIOGD_G_CONTEXT"
DIALOG_CONTEXT = "__AIOGD_D_CONTEXT"
DIALOG_INTERNAL_CONTEXT = "__AIOGD_ID_CONTEXT"

LAST_MESSAGE_ID = "LAST_MESSAGE_ID"


class DialogContext:
    def __init__(self, proxy: FSMContextProxy, dialog_id: str):
        self.proxy = proxy
        self.dialog_id = dialog_id

    @property
    def state(self) -> str:
        return self.proxy.state

    @state.setter
    def state(self, state: str):
        self.proxy.state = state

    @property
    def last_message_id(self) -> int:
        gcontext = self.proxy.get(GLOBAL_CONTEXT) or {}
        return gcontext.get(LAST_MESSAGE_ID)

    @last_message_id.setter
    def last_message_id(self, last_message_id: int):
        self.proxy[GLOBAL_CONTEXT][LAST_MESSAGE_ID] = last_message_id

    def set_data(self, key: str, value: Any, internal: bool = False):
        context_name = DIALOG_INTERNAL_CONTEXT if internal else DIALOG_CONTEXT
        self.proxy.setdefault(context_name, {})
        g_context = self.proxy[context_name]
        g_context.setdefault(self.dialog_id, {})
        g_context[self.dialog_id][key] = value

    def data(self, key, internal: bool = False):
        context_name = DIALOG_INTERNAL_CONTEXT if internal else DIALOG_CONTEXT
        gcontext = self.proxy.get(context_name) or {}
        dialog_data = gcontext.get(self.dialog_id) or {}
        return dialog_data[key]

    @classmethod
    async def create(cls, state: FSMContext, dialog_id: str):
        proxy = await FSMContextProxy.create(state)
        return cls(proxy, dialog_id)

    async def save(self):
        await self.proxy.save()

    def clear(self):
        if DIALOG_CONTEXT in self.proxy:
            if self.dialog_id in self.proxy[DIALOG_CONTEXT]:
                del self.proxy[DIALOG_CONTEXT][self.dialog_id]
        if DIALOG_INTERNAL_CONTEXT in self.proxy:
            if self.dialog_id in self.proxy[DIALOG_INTERNAL_CONTEXT]:
                del self.proxy[DIALOG_INTERNAL_CONTEXT][self.dialog_id]
