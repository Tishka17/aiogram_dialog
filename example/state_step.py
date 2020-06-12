import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message

from aiogram_dialog import Dialog, DataStep, StateStep

API_TOKEN = 'BOT TOKEN HERE'


class DialogSG(StatesGroup):
    name = State()
    eighteen = State()
    smoke = State()
    height = State()


async def input_done(m: Message, dialog_data, *args, **kwargs):
    if dialog_data['18+'] == 'yes':
        smoke_prefix = " не" if dialog_data["smoke"] == "no" else ""
        await m.answer(
            f"Спасибо за вашу анкету, {dialog_data['name']}. "
            f"Наверно, тяжело иметь рост {dialog_data['height']} после 18 лет и{smoke_prefix} "
            f"курить при этом"
        )
    else:
        await m.answer(
            f"Спасибо за вашу анкету, {dialog_data['name']}. "
            f"Наверно, тяжело иметь рост {dialog_data['height']}, когда ещё нет даже 18 лет")


dialog = Dialog(
    can_cancel=False,
    steps={
        DialogSG.name: DataStep(
            prompt="Введите ваше имя",
            field="name"
        ),
        DialogSG.eighteen: StateStep(
            prompt="Вам уже есть 18 лет?",
            variants=[
                ("Да", "yes", DialogSG.smoke),
                ("Нет", "no", DialogSG.height)
            ],
            reorder_variants_by=2,
            field="18+",
            type_factory=lambda x: x == "yes",
        ),
        DialogSG.smoke: DataStep(
            prompt="Вы курите?",
            variants=[
                ("Да", "yes"),
                ("Нет", "no")
            ],
            reorder_variants_by=2,
            field="smoke",
            type_factory=lambda x: x == "yes",
        ),
        DialogSG.height: DataStep(
            prompt="Введите ваш рост",
            error_msg="Ошибка, введите целое число!\n\n",
            type_factory=int,
            field="height",
            back=DialogSG.eighteen
        ),
    }
)

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

dialog.add_done_callback(input_done)
dialog.register_handler(dp)
dp.register_message_handler(dialog.start)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
