import asyncio
import logging
import os
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import (
    Dialog, LaunchMode, SubManager, Window, DialogManager, StartMode,
    setup_dialogs,
)
from aiogram_dialog.widgets.kbd import (
    Row, Checkbox, Radio, ManagedCheckboxAdapter,
    ListGroup,
)
from aiogram_dialog.widgets.text import Const, Format

API_TOKEN = os.getenv("BOT_TOKEN")


class DialogSG(StatesGroup):
    greeting = State()


def when_checked(data: Dict, widget, manager: SubManager) -> bool:
    # manager for our case is already adapted for current ListGroup row
    # so `.find` returns widget adapted for current row
    # if you need to find widgets outside the row, use `.find_in_parent`
    check: ManagedCheckboxAdapter = manager.find("check")
    return check.is_checked()


dialog = Dialog(
    Window(
        Const(
            "Hello, please check you options for each item:"
        ),
        ListGroup(
            Checkbox(
                Format("✓ {item}"),
                Format("  {item}"),
                id="check",
            ),
            Row(
                Radio(
                    Format("🔘 {item} ({data[item]})"),
                    Format("⚪️ {item} ({data[item]})"),
                    id="radio",
                    item_id_getter=str,
                    items=["black", "white"],
                    when=when_checked,
                )
            ),
            id="lg",
            item_id_getter=str,
            items=["apple", "orange", "pear"],

        ),
        state=DialogSG.greeting,
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
