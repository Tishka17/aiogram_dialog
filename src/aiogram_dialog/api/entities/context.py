from dataclasses import dataclass, field
from typing import Any, Optional, Union

from aiogram.fsm.state import State

from .access import AccessSettings

DataDict = dict[str, "Data"]
Data = Union[dict[str, DataDict], list[Any], int, str, float, None]


@dataclass(unsafe_hash=True)
class Context:
    _intent_id: str = field(compare=True)
    _stack_id: str = field(compare=True)
    state: State = field(compare=False)
    start_data: Data = field(compare=False)
    dialog_data: DataDict = field(compare=False, default_factory=dict)
    widget_data: DataDict = field(compare=False, default_factory=dict)
    access_settings: Optional[AccessSettings] = field(
        compare=False, default=None,
    )

    @property
    def id(self) -> str:
        return self._intent_id

    @property
    def stack_id(self) -> str:
        return self._stack_id
