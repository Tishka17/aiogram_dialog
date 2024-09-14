from typing import Any

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import (
    Dialog,
    DialogManager,
    Window,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Next
from aiogram_dialog.widgets.text import Const, Jinja


class SG(StatesGroup):
    age = State()
    country = State()
    result = State()


async def error(
        message: Message,
        dialog_: Any,
        manager: DialogManager,
        error_: ValueError
):
    await message.answer("Age must be a number!")


async def getter(dialog_manager: DialogManager, **kwargs):
    return {
        "age": dialog_manager.find("age").get_value(),
        "country": dialog_manager.find("country").get_value(),
    }


dialog = Dialog(
    Window(
        Const("Enter your country:"),
        TextInput(id="country", on_success=Next()),
        state=SG.country,
    ),
    Window(
        Const("Enter your age:"),
        TextInput(
            id="age",
            on_error=error,
            on_success=Next(),
            type_factory=int,
        ),
        state=SG.age,
    ),
    Window(
        Jinja(
            "<b>You entered</b>:\n\n"
            "<b>age</b>: {{age}}\n"
            "<b>country</b>: {{country}}\n"
        ),
        state=SG.result,
        getter=getter,
        parse_mode="html",
    ),
)
