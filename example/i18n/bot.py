"""
This is example of i18n with aiogram-dialog
To use it you need to install `fluent.runtime` package

Translation files are located in `translations` directory
"""

import asyncio
import logging
import os.path

from aiogram import Bot, Dispatcher
from aiogram.fsm.state import StatesGroup, State
from fluent.runtime import FluentResourceLoader, FluentLocalization

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window
from aiogram_dialog.widgets.kbd import Button, Row, Cancel
from i18n_format import I18NFormat
from i18n_middleware import I18nMiddleware


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


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()

    i18n_middleware = make_i18n_middleware()
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)

    registry = DialogRegistry()
    registry.register(dialog)
    registry.register_start_handler(DialogSG.greeting, dp)
    registry.setup(dp)

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
