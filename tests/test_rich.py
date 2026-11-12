import re
from datetime import datetime
from html import unescape
from typing import Any

import pytest
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import (
    AnswerCallbackQuery,
    EditMessageText,
    SendRichMessage,
    TelegramMethod,
)
from aiogram.types import (
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.test_tools import BotClient
from aiogram_dialog.test_tools.bot_client import FakeBot
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator
from aiogram_dialog.widgets.kbd import Next
from aiogram_dialog.widgets.rich import RichBlocks, RichHtml, RichMarkdown
from aiogram_dialog.widgets.text import Const


class MainSG(StatesGroup):
    html = State()
    markdown = State()
    blocks = State()
    plain = State()


dialog = Dialog(
    Window(
        Const("<b>html</b>"),
        Next(Const("Next")),
        rich=RichHtml(),
        state=MainSG.html,
    ),
    Window(
        Const("**markdown**"),
        Next(Const("Next")),
        rich=RichMarkdown(),
        state=MainSG.markdown,
    ),
    Window(
        Const("blocks"),
        Next(Const("Next")),
        rich=RichBlocks(),
        state=MainSG.blocks,
    ),
    Window(
        Const("plain"),
        state=MainSG.plain,
    ),
)


class RecordingBot(FakeBot):
    def __init__(self):
        self.requests: list[TelegramMethod[Any]] = []

    async def __call__(
            self, method: TelegramMethod[Any],
            request_timeout: int | None = None,
    ) -> Any:
        if isinstance(method, AnswerCallbackQuery):
            return True
        self.requests.append(method)
        return Message(
            message_id=1,
            date=datetime.fromtimestamp(1234567890),
            chat=Chat(id=1, type="private"),
        )


def html_callback_data(markup: str) -> str:
    return unescape(re.search('data="([^"]*)"', markup).group(1))


def message_with_button(callback_data: str) -> Message:
    return Message(
        message_id=1,
        date=datetime.fromtimestamp(1234567890),
        chat=Chat(id=1, type="private"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Next", callback_data=callback_data),
        ]]),
    )


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.html, mode=StartMode.RESET_STACK)


@pytest.mark.asyncio
async def test_rich_message():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())
    bot = RecordingBot()
    client = BotClient(dp, bot=bot)
    setup_dialogs(dp)
    next_button = InlineButtonTextLocator("Next")

    await client.send("/start")
    request = bot.requests[-1]
    assert isinstance(request, SendRichMessage)
    assert request.reply_markup is None
    assert request.rich_message.html.startswith(
        "<b>html</b><tg-button-row><tg-button",
    )
    callback_data = html_callback_data(request.rich_message.html)
    assert "\x7F" in callback_data

    await client.click(message_with_button(callback_data), next_button)
    request = bot.requests[-1]
    assert isinstance(request, EditMessageText)
    assert request.text is None
    assert request.reply_markup is None
    assert request.rich_message.markdown.startswith(
        "**markdown**\n\n<tg-button-row>",
    )
    callback_data = html_callback_data(request.rich_message.markdown)

    await client.click(message_with_button(callback_data), next_button)
    request = bot.requests[-1]
    assert isinstance(request, EditMessageText)
    paragraph, buttons = request.rich_message.blocks
    assert paragraph.text == "blocks"
    callback_data = buttons.buttons[0].callback_data
    assert "\x1D" in callback_data

    await client.click(message_with_button(callback_data), next_button)
    request = bot.requests[-1]
    assert isinstance(request, EditMessageText)
    assert request.text == "plain"
    assert request.rich_message is None
