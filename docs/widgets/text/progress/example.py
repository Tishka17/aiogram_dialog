import asyncio

from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Dialog, Window, DialogManager, BaseDialogManager
from aiogram_dialog.widgets.text import Multi, Const, Progress


class Main(StatesGroup):
    progress = State()


async def get_bg_data(dialog_manager: DialogManager, **kwargs):
    return {
        "progress": dialog_manager.dialog_data.get("progress", 0)
    }


async def background(manager: BaseDialogManager):
    count = 10
    for i in range(1, count + 1):
        await asyncio.sleep(1)
        await manager.update({
            "progress": i * 100 / count,
        })
    await asyncio.sleep(1)
    await manager.done()


dialog = Dialog(
    Window(
        Multi(
            Const("Your click is processing, please wait..."),
            Progress("progress", 10),
        ),
        state=Main.progress,
        getter=get_bg_data,
    ),
)


@dp.message(Command("start"))
async def start_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=Main.progress)
    asyncio.create_task(background(dialog_manager.bg()))
