import pytest
from aiogram.types import ChatAdministratorRights, ReplyKeyboardMarkup

from aiogram_dialog.widgets.kbd import Group, RequestChat, RequestUsers
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const


@pytest.mark.asyncio
async def test_render_request_users(mock_manager) -> None:
    kbd = RequestUsers(
        Const("Share"),
        request_id=1,
        user_is_bot=False,
        max_quantity=5,
        request_username=True,
    )

    keyboard = await kbd.render_keyboard(data={}, manager=mock_manager)

    button = keyboard[0][0]
    assert button.text == "Share"
    assert button.request_users.request_id == 1
    assert button.request_users.user_is_bot is False
    assert button.request_users.max_quantity == 5
    assert button.request_users.request_username is True
    assert button.request_users.user_is_premium is None


@pytest.mark.asyncio
async def test_render_request_chat(mock_manager) -> None:
    rights = ChatAdministratorRights.model_construct(can_manage_chat=True)
    kbd = RequestChat(
        Const("Pick chat"),
        request_id=2,
        chat_is_channel=True,
        bot_administrator_rights=rights,
        bot_is_member=True,
    )

    keyboard = await kbd.render_keyboard(data={}, manager=mock_manager)

    button = keyboard[0][0]
    assert button.text == "Pick chat"
    assert button.request_chat.request_id == 2
    assert button.request_chat.chat_is_channel is True
    assert button.request_chat.bot_administrator_rights == rights
    assert button.request_chat.bot_is_member is True
    assert button.request_chat.chat_is_forum is None


@pytest.mark.asyncio
async def test_request_buttons_in_reply_keyboard(mock_manager) -> None:
    kbd = Group(
        RequestUsers(Const("Users"), request_id=1),
        RequestChat(Const("Chat"), request_id=2, chat_is_channel=False),
    )
    factory = ReplyKeyboardFactory()

    raw = await kbd.render_keyboard(data={}, manager=mock_manager)
    markup = await factory.render_markup({}, mock_manager, raw)

    assert isinstance(markup, ReplyKeyboardMarkup)
    buttons = [button for row in markup.keyboard for button in row]
    assert buttons[0].request_users.request_id == 1
    assert buttons[1].request_chat.request_id == 2
