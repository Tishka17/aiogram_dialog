from dataclasses import dataclass, field
from typing import Dict, List, Union

from aiogram.fsm.state import State

SerializationData = Union[int, str, float, None]
Data = Union[Dict[SerializationData, "Data"], List["Data"], SerializationData]
DataDict = Dict[str, Data]


@dataclass(unsafe_hash=True)
class Context:
    _intent_id: str = field(compare=True)
    _stack_id: str = field(compare=True)
    state: State = field(compare=False)
    start_data: Data = field(compare=False)
    dialog_data: DataDict = field(compare=False, default_factory=dict)
    widget_data: DataDict = field(compare=False, default_factory=dict)

    @property
    def id(self) -> str:
        return self._intent_id

    @property
    def stack_id(self) -> str:
        return self._stack_id
