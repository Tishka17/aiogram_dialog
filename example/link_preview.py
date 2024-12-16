from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.link_preview import LinkPreview
from aiogram_dialog.widgets.text import Const, Format


async def photo_getter(**_):
    return {"photo_url": "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"}


class SG(StatesGroup):
    MAIN = State()
    IS_DISABLED = State()
    SMALL_MEDIA = State()
    LARGE_MEDIA = State()
    SHOW_ABOVE_TEXT = State()


BACK = SwitchTo(Const("back"), "_back", SG.MAIN)


dialog = Dialog(
    Window(
        Format("Default\n{photo_url}"),
        SwitchTo(
            Const("disable"), "_disable", SG.IS_DISABLED,
        ),
        SwitchTo(
            Const("prefer small media"), "_prefer_small_media", SG.SMALL_MEDIA,
        ),
        SwitchTo(
            Const("prefer large media"), "_prefer_large_media", SG.LARGE_MEDIA,
        ),
        SwitchTo(
            Const("show above text"), "_show_above_text", SG.SHOW_ABOVE_TEXT,
        ),
        getter=photo_getter,
        state=SG.MAIN,
    ),
    Window(
        Format("{photo_url}"),
        LinkPreview(is_disabled=True),
        BACK,
        state=SG.IS_DISABLED,
        getter=photo_getter,
    ),
    Window(
        Const("prefer small media"),
        LinkPreview(Format("{photo_url}"), prefer_small_media=True),
        BACK,
        state=SG.SMALL_MEDIA,
        getter=photo_getter,
    ),
    Window(
        Const("prefer large media"),
        LinkPreview(Format("{photo_url}"), prefer_large_media=True),
        BACK,
        state=SG.LARGE_MEDIA,
        getter=photo_getter,
    ),
    Window(
        Const("show above text"),
        LinkPreview(Format("{photo_url}"), show_above_text=True),
        BACK,
        state=SG.SHOW_ABOVE_TEXT,
        getter=photo_getter,
    ),
)

storage = MemoryStorage()
bot = Bot("token")
dp = Dispatcher(storage=storage)
dp.include_router(dialog)
setup_dialogs(dp)


@dp.message(Command("start"))
async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(SG.MAIN, mode=StartMode.RESET_STACK)


if __name__ == "__main__":
    dp.run_polling(bot, skip_updates=True)
