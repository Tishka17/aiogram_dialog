"""
This is example of i18n with aiogram-dialog
To use it you need to install `fluent.runtime` package

Translation files are located in i18n directory
"""

import asyncio
import logging
import os.path
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.middlewares import BaseMiddleware
from fluent.runtime import FluentResourceLoader, FluentLocalization

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window
from aiogram_dialog.widgets.kbd import Button, Row, Cancel
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.text.base import I18N_CONST_KEY
from aiogram_dialog.widgets.text.format import I18N_FORMAT_KEY

API_TOKEN = "PLACE YOUR TOKEN HERE"


class DialogSG(StatesGroup):
    greeting = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": "Username",
    }


dialog = Dialog(
    Window(
        Multi(
            Format("Hello-user"),
            sep="\n\n",
        ),
        Row(
            Button(Const("Demo-button"), id="demo"),
            Cancel(),
        ),
        getter=get_data,
        state=DialogSG.greeting,
    )
)


class I18nMiddleware(BaseMiddleware):
    def __init__(
            self,
            l10ns: Dict[str, FluentLocalization],
            default_lang: str,
    ):
        super().__init__()
        self.l10ns = l10ns
        self.default_lang = default_lang

    async def on_pre_process_message(self, event, data: dict):
        # some locale retriving logic
        lang = event.from_user.locale
        if lang in self.l10ns:
            l10n = self.l10ns[lang]
        else:
            l10n = self.l10ns[self.default_lang]

        # we use fluent.runtime here, but you can create custom functions
        data[I18N_FORMAT_KEY] = l10n.format_value
        data[I18N_CONST_KEY] = l10n.format_value

    on_pre_process_callback_query = on_pre_process_message
    on_pre_process_aiogd_update = on_pre_process_message
    on_pre_process_my_chat_member = on_pre_process_message


DEFAULT_LOCALE = "en"
LOCALES = ["en"]


def make_i18n_middleware():
    loader = FluentResourceLoader(os.path.join(
        os.path.dirname(__file__),
        "i18n",
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
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    dp.setup_middleware(make_i18n_middleware())
    registry = DialogRegistry(dp)
    registry.register_start_handler(DialogSG.greeting)
    registry.register(dialog)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
