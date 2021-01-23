import asyncio
from pprint import pprint

from dialog.kbd import Button, Group
from dialog.text import Const, Format, Multi
from dialog.window import Window


async def get_data():
    return {"name": "Tishka17", "age": 19}


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
                Button(Format("1. {name}"), Format("b1_{name}")),
                Button(Const("2. {name}"), Format("b2_{name}")),
                keep_rows=False
            ),
            Button(Const("3. {name}"), Const("b3_{name}")),
        ),
        getter=get_data
    )

    data = await window.load_data()
    res = await window.render_text(data)
    print(res)
    res = await window.render_kbd(data)
    pprint(res.inline_keyboard)


if __name__ == '__main__':
    asyncio.run(main())
