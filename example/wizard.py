import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from aiogram_dialog import (
    Dialog, DialogManager, setup_dialogs, StartMode, Window,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Checkbox, Next, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja


class Wizard(StatesGroup):
    title = State()
    description = State()
    options = State()
    preview = State()


FINISHED_KEY = "finished"

CANCEL_EDIT = SwitchTo(
    Const("Отменить редактирование"),
    when=F["dialog_data"][FINISHED_KEY],
    id="cnl_edt",
    state=Wizard.preview,
)


async def next_or_end(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get(FINISHED_KEY):
        await dialog_manager.switch_to(Wizard.preview)
    else:
        await dialog_manager.next()


async def result_getter(dialog_manager: DialogManager, **kwargs):
    dialog_manager.dialog_data[FINISHED_KEY] = True
    options = []
    if dialog_manager.find("pink").is_checked():
        options.append("Розовые")
    if dialog_manager.find("glitter").is_checked():
        options.append("Блестки")
    if dialog_manager.find("bow").is_checked():
        options.append("С бантиком")
    return {
        "options": options,
        "title": dialog_manager.find("title").get_value(),
        "description": dialog_manager.find("description").get_value(),
    }


dialog = Dialog(
    Window(
        Const("Введите название"),
        TextInput(id="title", on_success=next_or_end),
        CANCEL_EDIT,
        state=Wizard.title,
    ),
    Window(
        Const("Введите описание"),
        TextInput(id="description", on_success=next_or_end),
        CANCEL_EDIT,
        state=Wizard.description,
    ),
    Window(
        Const("Выберите опции"),
        Checkbox(Const("✓ Розовый"), Const("Розовый"), id="pink"),
        Checkbox(Const("✓ Блестки"), Const("Блестки"), id="glitter"),
        Checkbox(Const("✓ С бантиком"), Const("С бантиком"), id="bow"),
        Next(Const("Далее")),
        CANCEL_EDIT,
        state=Wizard.options,
    ),
    Window(
        Jinja(
            "<u>Вы ввели</u>:\n\n"
            "<b>Название</b>: {{title}}\n"
            "<b>Описание</b>: {{description}}\n"
            "<b>Опции</b>: \n"
            "{% for item in options %}"
            "• {{item}}\n"
            "{% endfor %}",
        ),
        SwitchTo(
            Const("Изменить название"),
            state=Wizard.title, id="to_title",
        ),
        SwitchTo(
            Const("Изменить описание"),
            state=Wizard.description, id="to_desc",
        ),
        SwitchTo(
            Const("Изменить опции"),
            state=Wizard.options, id="to_opts",
        ),
        state=Wizard.preview,
        getter=result_getter,
        parse_mode="html",
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(Wizard.title, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
