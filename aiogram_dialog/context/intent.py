import warnings
from dataclasses import dataclass, field
from typing import Union, Dict, List

from aiogram.dispatcher.filters.state import State

Data = Union[Dict, List, int, str, None]
DataDict = Dict[str, Data]


@dataclass(unsafe_hash=True)
class Intent:
    _id: str = field(compare=True)
    _stack_id: str = field(compare=True)
    state: State = field(compare=False)
    start_data: Data = field(compare=False)
    dialog_data: DataDict = field(compare=False, default_factory=dict)
    widget_data: DataDict = field(compare=False, default_factory=dict)

    @property
    def id(self):
        return self._id

    @property
    def stack_id(self):
        return self._stack_id

    @property
    def data(self):
        warnings.warn(
            "use `intent.start_data` instead",
            DeprecationWarning
        )
        return self.start_data