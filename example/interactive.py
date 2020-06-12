import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message

from aiogram_dialog import Dialog, DataStep

API_TOKEN = 'BOT TOKEN HERE'


class NamedStep(DataStep):
    async def render_text(self, current_data, error: Optional[Exception], *args, **kwargs):
        prefix = self.error_msg if error else ""
        prefix = prefix + f"{current_data['name']},\n"
        return prefix + self.prompt


class InpuDialog(Dialog):
    def __init__(self):
        super().__init__(steps={
            State("1"): DataStep(
                prompt="Введите ваше имя",
                field="name"
            ),
            State("2"): NamedStep(
                prompt="Вам уже есть 18 лет?",
                variants=[
                    ("Да", "yes"),
                    ("Нет", "no")
                ],
                reorder_variants_by=2,
                field="18+",
            ),
            State("3"): NamedStep(
                prompt="Введите ваш рост",
                error_msg="Ошибка, введите целое число!\n\n",
                type_factory=int,
                field="height",
            ),
        })

    async def on_done(self, m: Message, dialog_data, *args, **kwargs):
        if dialog_data['18+'] == 'yes':
            await m.answer(
                f"Спасибо за вашу анкету, {dialog_data['name']}. "
                f"Наверно, тяжело иметь рост {dialog_data['height']} после 18 лет")
        else:
            await m.answer(
                f"Спасибо за вашу анкету, {dialog_data['name']}. "
                f"Наверно, тяжело иметь рост {dialog_data['height']}, когда ещё нет даже 18 лет")


async def main():
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)

    dialog = InpuDialog()
    dialog.register_handler(dp)
    dp.register_message_handler(dialog.start)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
