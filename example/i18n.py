import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.middlewares import BaseMiddleware

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Back
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
            Format("{name}! Thank you for your answers."),
            sep="\n\n",
        ),
        Row(
            Back(),
            SwitchTo(Const("Restart"), id="restart", state=DialogSG.greeting),
            Button(Const("Finish"), id="finish"),
        ),
        getter=get_data,
        state=DialogSG.greeting,
    )
)


class I18nMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, event, data: dict):
        # some locale retriving logic
        try:
            lang = event.from_user.locale
        except AttributeError:
            lang = "en"

        # simulate some translation logic
        # you can use fluent-runtime FluentLocalization.format instead
        def format_text(msg, values):
            res = msg.format_map(values)
            return f"{res} \n/{lang}"

        def const_text(msg, values):
            return f"{msg} \n/{lang}"

        data[I18N_FORMAT_KEY] = format_text
        data[I18N_CONST_KEY] = const_text

    on_pre_process_callback_query = on_pre_process_message
    on_pre_process_aiogd_update = on_pre_process_message
    on_pre_process_my_chat_member = on_pre_process_message


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    dp.setup_middleware(I18nMiddleware())
    registry = DialogRegistry(dp)
    registry.register_start_handler(DialogSG.greeting)
    registry.register(dialog)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
