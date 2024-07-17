from dataclasses import dataclass
from typing import Any, List, Optional

from aiogram.enums import ChatMemberStatus


@dataclass
class AccessSettings:
    user_ids: List[int]
    member_status: Optional[ChatMemberStatus] = None
    custom: Any = None
