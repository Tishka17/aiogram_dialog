import asyncio
import logging
import os.path
from io import BytesIO
from typing import Union


from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, ContentType, InputFile, Message
from PIL import Image, ImageDraw, ImageFont


from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs,
    StartMode, Window,
)
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.manager.message_manager import MessageManager
from aiogram_dialog.widgets.kbd import Back, Next, Row
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const


src_dir = os.path.normpath(os.path.join(__file__, os.path.pardir))

API_TOKEN = os.getenv("BOT_TOKEN")
CUSTOM_URL_PREFIX = "my://"


def draw(text) -> bytes:
    logging.info("Draw image")
    img = Image.new("RGB", (200, 100), 0x800000)
    draw = ImageDraw.Draw(img)

    fontsize = 40
    try:
        font = ImageFont.truetype("FreeSans.ttf", size=fontsize)
    except OSError:
        font = ImageFont.truetype("arial.ttf", size=fontsize)
    width = font.getlength(text)
    draw.text((100 - width / 2, 10), str(text), font=font)

    io = BytesIO()
    img.save(io, "PNG")
    io.seek(0)
    return io.read()


class DialogSG(StatesGroup):
    custom = State()
    custom2 = State()
    normal = State()


class CustomMessageManager(MessageManager):
    async def get_media_source(
        self, media: MediaAttachment, bot: Bot,
    ) -> Union[InputFile, str]:
        if media.file_id:
            return await super().get_media_source(media, bot)
        if media.url and media.url.startswith(CUSTOM_URL_PREFIX):
            text = media.url[len(CUSTOM_URL_PREFIX):]
            return BufferedInputFile(draw(text), f"{text}.png")
        return await super().get_media_source(media, bot)


dialog = Dialog(
    Window(
        Const("Custom image:"),
        StaticMedia(
            url="my://text",
            type=ContentType.PHOTO,
        ),
        Next(),
        state=DialogSG.custom,
    ),
    Window(
        Const("Another custom image:"),
        StaticMedia(
            url="my://another",
            type=ContentType.PHOTO,
        ),
        Row(Back(), Next()),
        state=DialogSG.custom2,
    ),
    Window(
        Const("Normal image:"),
        StaticMedia(
            path=os.path.join(src_dir, "python_logo.png"),
            type=ContentType.PHOTO,
        ),
        Back(),
        state=DialogSG.normal,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(DialogSG.custom, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)

    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    dp.include_router(dialog)
    setup_dialogs(dp, message_manager=CustomMessageManager())

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
