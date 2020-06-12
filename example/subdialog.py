import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State

from aiogram_dialog import Dialog, DataStep, StateStep

API_TOKEN = 'BOT TOKEN HERE'

subdialog = Dialog(steps={
    State("subdialog"): DataStep(
        prompt="Вы курите?",
        variants=[
            ("Да", "yes"),
            ("Нет", "no")
        ],
        reorder_variants_by=2,
        field="smoke",
        type_factory=lambda x: x == "yes",
    ),
})

last_state = State("empty")
dialog = Dialog(
    can_done=True,
    can_cancel=False,
    can_back=False,
    steps={
        State("dialog"): StateStep(
            prompt="Вам уже есть 18 лет?",
            variants=[
                ("Да", "yes", subdialog),
                ("Нет", "no", last_state)
            ],
            reorder_variants_by=2,
            field="18+",
            type_factory=lambda x: x == "yes",
        ),
        last_state: DataStep(
            prompt="Спасибо",
            allow_text=False,
        )
    }
)

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

dialog.register_handler(dp)
subdialog.register_handler(dp)
subdialog.add_finished_callback(dialog.resume)
dp.register_message_handler(dialog.start)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
