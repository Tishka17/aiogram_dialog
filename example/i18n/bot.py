"""
This is example of i18n with aiogram-dialog.

To use it you need to install `fluent.runtime` package
Translation files are located in `translations` directory
"""

import asyncio
import logging
import os.path

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from fluent.runtime import FluentLocalization, FluentResourceLoader
from i18n_format import I18NFormat
from i18n_middleware import I18nMiddleware

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window
)
from aiogram_dialog.widgets.kbd import Button, Cancel, Row


class DialogSG(StatesGroup):
    greeting = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    name = dialog_manager.event.from_user.full_name
    return {
        "name": name,
    }


dialog = Dialog(
    Window(
        I18NFormat("Hello-user"),
        Row(
            Button(I18NFormat("Demo-button"), id="demo"),
            Cancel(text=I18NFormat("Cancel")),
        ),
        getter=get_data,
        state=DialogSG.greeting,
    )
)

DEFAULT_LOCALE = "en"
LOCALES = ["en"]


def make_i18n_middleware():
    loader = FluentResourceLoader(os.path.join(
        os.path.dirname(__file__),
        "translations",
        "{locale}",
    ))
    l10ns = {
        locale: FluentLocalization(
            [locale, DEFAULT_LOCALE], ["main.ftl"], loader,
        )
        for locale in LOCALES
    }
    return I18nMiddleware(l10ns, DEFAULT_LOCALE)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()

    i18n_middleware = make_i18n_middleware()
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)

    dp.include_router(dialog)
    dp.message.register(start, CommandStart())
    setup_dialogs(dp)

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
