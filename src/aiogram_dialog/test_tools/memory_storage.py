import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional, Union

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey

StateType = Optional[Union[str, State]]


@dataclass
class MemoryStorageRecord:
    data: str = "{}"
    state: Optional[str] = None


class JsonMemoryStorage(BaseStorage):
    storage: dict[StorageKey, MemoryStorageRecord]

    def __init__(self) -> None:
        self.storage = defaultdict(MemoryStorageRecord)

    async def close(self) -> None:
        pass

    async def set_state(
            self, key: StorageKey, state: StateType = None,
    ) -> None:
        if isinstance(state, State):
            state_value = state.state
        else:
            state_value = state
        self.storage[key].state = state_value

    async def get_state(self, key: StorageKey) -> Optional[str]:
        return self.storage[key].state

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        self.storage[key].data = json.dumps(data)

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return json.loads(self.storage[key].data)
