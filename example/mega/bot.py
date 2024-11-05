import asyncio
import logging
import os.path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent, Message, ReplyKeyboardRemove
from bot_dialogs import states
from bot_dialogs.calendar import calendar_dialog
from bot_dialogs.counter import counter_dialog
from bot_dialogs.layouts import layouts_dialog
from bot_dialogs.main import main_dialog
from bot_dialogs.mutltiwidget import multiwidget_dialog
from bot_dialogs.reply_buttons import reply_kbd_dialog
from bot_dialogs.scrolls import scroll_dialog
from bot_dialogs.select import selects_dialog
from bot_dialogs.switch import switch_dialog

from aiogram_dialog import DialogManager, ShowMode, StartMode, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(
        states.Main.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager):
    # Example of handling UnknownIntent Error and starting new dialog.
    logging.error("Restarting dialog: %s", event.exception)
    if event.update.callback_query:
        await event.update.callback_query.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
        )
        if event.update.callback_query.message:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass  # whatever
    elif event.update.message:
        await event.update.message.answer(
            "Bot process was restarted due to maintenance.\n"
            "Redirecting to main menu.",
            reply_markup=ReplyKeyboardRemove(),
        )
    await dialog_manager.start(
        states.Main.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


dialog_router = Router()
dialog_router.include_routers(
    layouts_dialog,
    scroll_dialog,
    main_dialog,
    calendar_dialog,
    selects_dialog,
    counter_dialog,
    multiwidget_dialog,
    switch_dialog,
    reply_kbd_dialog,
)


def setup_dp():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.register(start, F.text == "/start")
    dp.business_message.register(start, F.text == "/start")
    dp.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.include_router(dialog_router)
    setup_dialogs(dp)
    return dp


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = setup_dp()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
