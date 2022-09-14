from typing import Literal

from aiogram.types import (
    Chat,
    User,
)


class FakeUser(User):
    fake: Literal[True] = True


class FakeChat(Chat):
    fake: Literal[True] = True
