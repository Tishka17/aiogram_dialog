import asyncio
from pprint import pprint

from aiogram.dispatcher.filters.state import StatesGroup, State

from dialog.dialog import Dialog
from dialog.kbd import Button, Group
from dialog.text import Const, Format, Multi
from dialog.window import Window


async def get_data():
    return {"name": "Tishka17", "age": 19}


class Register(StatesGroup):
    hello = State()
    name = State()


async def main():
    window = Window(
        Multi(
            Const("Hello, {name}!"),
            Format("Hello, {name}!"),
            sep="\n\n",
            when=lambda data: data["age"] > 18,
        ),
        Group(
            Group(
                Button(Format("1. {name}"), "b1"),
                Button(Const("2. {name}"), "b2"),
                keep_rows=False
            ),
            Button(Const("3. {name}"), "b3"),
        ),
        getter=get_data,
        state=Register.hello,

    )

    data = await window.load_data()
    res = await window.render_text(data)
    print(res)
    res = await window.render_kbd(data)
    pprint(res.inline_keyboard)

    # todo
    dialog = Dialog(window)


if __name__ == '__main__':
    asyncio.run(main())
