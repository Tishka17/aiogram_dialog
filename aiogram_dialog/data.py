from typing import Any, Optional, Type

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContextProxy

GLOBAL_CONTEXT = "__AIOGD_G_CONTEXT"
DIALOG_CONTEXT = "__AIOGD_D_CONTEXT"
DIALOG_INTERNAL_CONTEXT = "__AIOGD_ID_CONTEXT"

LAST_MESSAGE_ID = "LAST_MESSAGE_ID"

FORBID = object()


def reset_dialog_contexts(proxy: FSMContextProxy):
    proxy.pop(DIALOG_CONTEXT, None)
    proxy.pop(DIALOG_INTERNAL_CONTEXT, None)


class DialogContext:
    def __init__(self, proxy: FSMContextProxy, dialog_id: str, states_group: Optional[Type[StatesGroup]]):
        self.proxy = proxy
        self.dialog_id = dialog_id
        self.states_group = states_group

    @property
    def state(self) -> State:
        if not self.states_group:
            raise ValueError("No states group in current context")
        state = self.proxy.state
        for s in self.states_group.states:
            if s.state == state:
                return s
        raise ValueError("Unknown state `%s`" % state)

    @state.setter
    def state(self, state: State):
        self.proxy.state = state.state

    @property
    def last_message_id(self) -> Optional[int]:
        gcontext = self.proxy.get(GLOBAL_CONTEXT) or {}
        return gcontext.get(LAST_MESSAGE_ID)

    @last_message_id.setter
    def last_message_id(self, last_message_id: int):
        self.proxy.setdefault(GLOBAL_CONTEXT, {})
        g_context = self.proxy[GLOBAL_CONTEXT]
        g_context[LAST_MESSAGE_ID] = last_message_id

    def set_data(self, key: str, value: Any, *, internal: bool = False):
        context_name = DIALOG_INTERNAL_CONTEXT if internal else DIALOG_CONTEXT
        self.proxy.setdefault(context_name, {})
        d_context = self.proxy[context_name]
        d_context.setdefault(self.dialog_id, {})
        d_context[self.dialog_id][key] = value

    def data(self, key, default=FORBID, *, internal: bool = False, ):
        context_name = DIALOG_INTERNAL_CONTEXT if internal else DIALOG_CONTEXT
        d_context = self.proxy.get(context_name) or {}
        dialog_data = d_context.get(self.dialog_id) or {}
        if default is FORBID:
            return dialog_data[key]
        else:
            return dialog_data.get(key, default)

    def clear(self):
        if DIALOG_CONTEXT in self.proxy:
            if self.dialog_id in self.proxy[DIALOG_CONTEXT]:
                del self.proxy[DIALOG_CONTEXT][self.dialog_id]
        if DIALOG_INTERNAL_CONTEXT in self.proxy:
            if self.dialog_id in self.proxy[DIALOG_INTERNAL_CONTEXT]:
                del self.proxy[DIALOG_INTERNAL_CONTEXT][self.dialog_id]
