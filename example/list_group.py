import asyncio
import logging
import os
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram_dialog import (
    Dialog, DialogRegistry, LaunchMode, SubManager, Window,
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


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    registry = DialogRegistry()
    registry.register(dialog)

    registry.register_start_handler(state=DialogSG.greeting, router=dp)
    registry.setup_dp(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
