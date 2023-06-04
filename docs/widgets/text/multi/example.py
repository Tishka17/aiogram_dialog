from aiogram_dialog.widgets.text import Multi, Const, Format


# let's assume this is our window data getter
async def get_data(**kwargs):
    return {"name": "Tishka17"}


# This will produce text `Hello! And goodbye!`
text = Multi(
    Const("Hello!"),
    Const("And goodbye!"),
    sep=" ",
)

# This one will produce text `Hello, Tishka17, and goodbye {name}!`
text2 = Multi(
    Format("Hello, {name}"),
    Const("and goodbye {name}!"),
    sep=", ",
)

# This one will produce `01.02.2003T04:05:06`
text3 = Multi(
    Multi(Const("01"), Const("02"), Const("2003"), sep="."),
    Multi(Const("04"), Const("05"), Const("06"), sep=":"),
    sep="T"
)
