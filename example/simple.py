import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, DialogRegistry, Window, ChatEvent
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchState, Back
from aiogram_dialog.widgets.text import Const, Format, Multi

API_TOKEN = "PLACE YOUR TOKEN HERE"


class DialogSG(StatesGroup):
    greeting = State()
    age = State()
    finish = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    age_select: Select = dialog_manager.dialog().find("w_age")
    age = age_select.get_checked(dialog_manager)
    return {
        "name": dialog_manager.context.data("name", ""),
        "age": age,
        "can_smoke": age in ("18-25", "25-40", "40+"),
    }


async def name_handler(m: Message, dialog: Dialog, manager: DialogManager):
    manager.context.set_data("name", m.text)
    await m.answer(f"Nice to meet you, {m.text}")
    await dialog.next(manager)


async def on_finish(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.answer("Thank you. To start again click /start")
    await manager.done()


async def on_age_changed(c: ChatEvent, item_id: str, select: Select, manager: DialogManager):
    await manager.dialog().next(manager)


dialog = Dialog(
    Window(
        text=Const("Greetings! Please, introduce yourself:"),
        kbd=None,
        state=DialogSG.greeting,
        on_message=name_handler,
    ),
    Window(
        text=Format("{name}! How old are you?"),
        kbd=Select(
            checked_text=Format("✓ {item}"), unchecked_text=Format("{item}"),
            items=["0-12", "12-18", "18-25", "25-40", "40+"],
            item_id_getter=lambda x: x,
            min_selected=1,
            id="w_age",
            on_state_changed=on_age_changed,
        ),
        state=DialogSG.age,
        getter=get_data,
    ),
    Window(
        text=Multi(
            Format("{name}! Thank you for your answers."),
            Const("Hope you are not smoking", when="can_smoke"),
            sep="\n\n",
        ),
        kbd=Row(
            Back(),
            SwitchState(Const("Restart"), id="restart", state=DialogSG.greeting),
            Button(Const("Finish"), on_click=on_finish, id="finish"),
        ),
        getter=get_data,
        state=DialogSG.finish,
    )
)


async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.greeting)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    registry.register(dialog)
    dp.register_message_handler(start, text="/start", state="*")

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
