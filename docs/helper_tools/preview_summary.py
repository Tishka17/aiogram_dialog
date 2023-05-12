import asyncio

from aiogram import Dispatcher
from aiogram.filters.state import StatesGroup, State

from aiogram_dialog import Dialog, Window
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

dp = Dispatcher()
dp.include_router(dialog)


async def main():
    await render_preview(dp, "preview.html")


if __name__ == '__main__':
    asyncio.run(main())
