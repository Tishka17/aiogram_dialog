from dataclasses import dataclass
from typing import Any, List


@dataclass
class AccessSettings:
    user_ids: List[int]
    custom: Any = None
