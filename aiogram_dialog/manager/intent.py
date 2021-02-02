from dataclasses import dataclass
from typing import Dict, Union, List

Data = Union[Dict, List, int, str, None]


@dataclass(frozen=True)
class Intent:
    id: str
    name: str
    data: Data
