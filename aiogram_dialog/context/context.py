import warnings
from dataclasses import dataclass, field
from typing import Dict

from aiogram.dispatcher.fsm.state import State

from .events import Data

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
    def id(self):
        return self._intent_id

    @property
    def stack_id(self):
        return self._stack_id

    @property
    def data(self):
        warnings.warn(
            "use `context.start_data` instead",
            DeprecationWarning
        )
        return self.start_data
