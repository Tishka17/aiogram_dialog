from aiogram.types import Chat, User

from aiogram_dialog.api.internal import FakeChat, FakeUser
from aiogram_dialog.utils import is_chat_loaded, is_user_loaded


def test_is_chat_loaded():
    assert is_chat_loaded(Chat(id=1, type="private"))
    assert not is_chat_loaded(FakeChat(id=1, type="private"))


def test_is_user_loaded():
    assert is_user_loaded(User(id=1, is_bot=False, first_name=""))
    assert not is_user_loaded(FakeUser(id=1, is_bot=False, first_name=""))
