import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.types import CallbackQuery, Message

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, NumberedPager, StubScroll
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format


class Medias(StatesGroup):
    start = State()


async def on_input_photo(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data.setdefault("photos", []).append(
        (message.photo[-1].file_id, message.photo[-1].file_unique_id),
    )


async def on_delete(
        callback: CallbackQuery, widget: Button, dialog_manager: DialogManager,
):
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    del photos[media_number]
    if media_number > 0:
        await scroll.set_page(media_number - 1)


async def getter(dialog_manager: DialogManager, **kwargs) -> dict:
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    if photos:
        photo = photos[media_number]
        media = MediaAttachment(
            file_id=MediaId(*photo),
            type=ContentType.PHOTO,
        )
    else:
        media = MediaAttachment(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Image_not_available.png/800px-Image_not_available.png?20210219185637",  # noqa: E501
            type=ContentType.PHOTO,
        )
    return {
        "media_count": len(photos),
        "media_number": media_number + 1,
        "media": media,
    }


dialog = Dialog(Window(
    Const("Send media"),
    DynamicMedia(selector="media"),
    StubScroll(id="pages", pages="media_count"),
    Group(
        NumberedPager(scroll="pages", when=F["pages"] > 1),
        width=8,
    ),
    Button(
        Format("🗑️ Delete photo #{media_number}"),
        id="del",
        on_click=on_delete,
        when="media_count",
        # Alternative F['media_count']
    ),
    MessageInput(content_types=[ContentType.PHOTO], func=on_input_photo),
    getter=getter,
    state=Medias.start,
))


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(Medias.start, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dp.include_router(dialog)

    dp.message.register(start, CommandStart())
    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
