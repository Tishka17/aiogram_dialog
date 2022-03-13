import asyncio
import logging
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

from aiogram_dialog import (
    Dialog, DialogManager, DialogRegistry, Window, )
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.kbd import (
    Row, Checkbox, Radio, ManagedCheckboxAdapter,
)
from aiogram_dialog.widgets.kbd.list_group import (
    ListGroup, ManagedListGroupAdapter,
)
from aiogram_dialog.widgets.text import Const, Format

API_TOKEN = "PLACE YOUR TOKEN HERE"


class DialogSG(StatesGroup):
    greeting = State()


def when_checked(data: Dict, widget, manager: DialogManager) -> bool:
    lg: ManagedListGroupAdapter = manager.dialog().find("lg")
    # normally we need to get id from `data["item"]`
    check: ManagedCheckboxAdapter = lg.find_for_item("check", data["item"])
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
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    registry.register_start_handler(DialogSG.greeting)
    registry.register(dialog)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
