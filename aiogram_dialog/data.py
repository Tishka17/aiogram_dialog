from typing import Optional, Union, Dict

from aiogram.dispatcher import FSMContext

NOT_FILLED = object()


class DialogData:
    STATE_FIELD = "old_state"
    MSG_FIELD = "last_message"
    DATA_FIELD = "data"

    def __init__(self, dialog_field: Optional[str], state: FSMContext):
        self.dialog_field = dialog_field
        self.state = state
        self.field_changes = {}
        self.field_deletes = set()
        self.changes = {}
        self._data: Union[Dict, NOT_FILLED] = NOT_FILLED  # cache of field data

    def _dialog_data(self, data):
        if not self.dialog_field:
            return data
        field_data = data.get(self.dialog_field)
        if not field_data:
            field_data = {}
            data[self.dialog_field] = field_data
        return field_data

    async def set_old_state(self):
        self.changes[self.STATE_FIELD] = await self.state.get_state()

    async def old_state(self) -> Optional[str]:
        data = await self.state.get_data()
        return self._dialog_data(data).get(self.STATE_FIELD)

    def set_message_id(self, msg_id: int):
        self.changes[self.MSG_FIELD] = msg_id

    async def message_id(self) -> Optional[int]:
        data = await self.state.get_data()
        return self._dialog_data(data).get(self.MSG_FIELD)

    def update(self, data):
        if data:
            self.field_changes.update(data)

    def __setitem__(self, key, value):
        if not key:
            return
        self.field_changes[key] = value
        if self._data not in (None, NOT_FILLED):
            self._data[key] = value
        self.field_deletes.discard(key)

    def __delitem__(self, key):
        if not key:
            return
        if self._data not in (None, NOT_FILLED):
            self._data.pop(key, None)
        self.field_changes.pop(key, None)
        self.field_deletes.add(key)

    async def reset(self):
        async with self.state.proxy() as data:
            dialog_data = self._dialog_data(data)
            old_state = dialog_data.get(self.STATE_FIELD)
            if self.dialog_field:
                del data[self.dialog_field]
            else:
                data.clear()
        await self.state.set_state(old_state)
        self.changes = {}
        self.field_changes = {}

    async def commit(self):
        if not self.changes and not self.field_changes and not self.field_deletes:
            return
        async with self.state.proxy() as state_data:
            data = self._dialog_data(state_data)
            data.update(self.changes)
            field_data = data.get(self.DATA_FIELD)
            if self.field_changes:
                if not field_data:
                    data[self.DATA_FIELD] = self.field_changes
                else:
                    field_data.update(self.field_changes)
            if self.field_deletes and field_data:
                field_data = data.get(self.DATA_FIELD)
                for field in self.field_deletes:
                    field_data.pop(field, None)
        self.changes = {}
        self.field_changes = {}
        self.field_deletes = set()

    async def data(self, force: bool = False):
        if not force and self._data != NOT_FILLED:
            result = self._data
        else:
            async with self.state.proxy() as data:
                data = self._dialog_data(data)
                result = data.get(self.DATA_FIELD) or {}
        result.update(self.field_changes)
        self._data = result
        return self._data
