from dataclasses import dataclass, field
from typing import Dict, Union, List

Data = Union[Dict, List, int, str, None]


@dataclass(frozen=True)
class Intent:
    id: str = field(compare=True)
    name: str = field(compare=False)
    data: Data = field(compare=False)
