import pytest
from aiogram.types import (
    Chat,
    CopyTextButton,
    InlineKeyboardButton,
    RichTextCustomEmoji,
    User,
)

from aiogram_dialog.api.internal import FakeChat, FakeUser
from aiogram_dialog.utils import (
    is_chat_loaded,
    is_user_loaded,
    remove_intent_id,
    transform_to_rich_blocks,
    transform_to_rich_html,
)


def test_is_chat_loaded():
    assert is_chat_loaded(Chat(id=1, type="private"))
    assert not is_chat_loaded(FakeChat(id=1, type="private"))


def test_is_user_loaded():
    assert is_user_loaded(User(id=1, is_bot=False, first_name=""))
    assert not is_user_loaded(FakeUser(id=1, is_bot=False, first_name=""))


def test_remove_intent_id():
    assert remove_intent_id("intent\x1Dbutton") == ("intent", "button")
    assert remove_intent_id("intent\x7Fbutton") == ("intent", "button")
    assert remove_intent_id("intent\x1Db\x7Fx") == ("intent", "b\x7Fx")
    assert remove_intent_id("button") == (None, "button")


def test_transform_to_rich_html():
    keyboard = [
        [
            InlineKeyboardButton(
                text="<Next>", callback_data="intent\x1Dnext", style="success",
            ),
            InlineKeyboardButton(text="Url", url="https://t.me/?a=1&b=2"),
        ],
        [],
        [
            InlineKeyboardButton(
                text="Copy", copy_text=CopyTextButton(text='"text"'),
                icon_custom_emoji_id="123",
            ),
        ],
    ]
    assert transform_to_rich_html(keyboard) == (
        "<tg-button-row>"
        '<tg-button type="callback_data" data="intent\x7Fnext" '
        'style="success">&lt;Next&gt;</tg-button>'
        '<tg-button type="url" url="https://t.me/?a=1&amp;b=2">Url</tg-button>'
        "</tg-button-row>"
        "<tg-button-row>"
        '<tg-button type="copy_text" text="&quot;text&quot;">'
        '<tg-emoji emoji-id="123"></tg-emoji>Copy</tg-button>'
        "</tg-button-row>"
    )


def test_transform_to_rich_blocks():
    keyboard = [
        [InlineKeyboardButton(text="Next", callback_data="intent\x1Dnext")],
        [],
        [InlineKeyboardButton(text="Url", url="https://t.me", style="danger")],
        [InlineKeyboardButton(
            text="Emoji", icon_custom_emoji_id="123", url="https://t.me",
        )],
    ]
    first, second, third = transform_to_rich_blocks(keyboard)
    assert first.buttons[0].text == "Next"
    assert first.buttons[0].callback_data == "intent\x1Dnext"
    assert second.buttons[0].url == "https://t.me"
    assert second.buttons[0].style == "danger"
    assert third.buttons[0].text == [
        RichTextCustomEmoji(custom_emoji_id="123", alternative_text=""),
        "Emoji",
    ]


@pytest.mark.parametrize("transform", [
    transform_to_rich_html,
    transform_to_rich_blocks,
])
def test_transform_pay_button_to_rich(transform):
    keyboard = [[InlineKeyboardButton(text="Pay", pay=True)]]
    with pytest.raises(ValueError, match="pay or game"):
        transform(keyboard)
