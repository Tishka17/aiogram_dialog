import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram_dialog import Dialog, DialogRegistry, Window
from aiogram_dialog.tools import render_preview
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Format


class RenderSG(StatesGroup):
    first = State()


dialog = Dialog(
    Window(
        Format("Hello, {name}"),
        Cancel(),
        state=RenderSG.first,
        preview_data={"name": "Tishka17"},
    ),
)

storage = MemoryStorage()
bot = Bot(token='BOT TOKEN HERE')
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)
registry.register(dialog)


async def main():
    await render_preview(registry, "preview.html")


if __name__ == '__main__':
    asyncio.run(main())
