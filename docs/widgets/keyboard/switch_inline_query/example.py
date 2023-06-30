from aiogram_dialog.widgets.kbd import SwitchInlineQuery
from aiogram_dialog.widgets.text import Const

switch_query = SwitchInlineQuery(
    Const("Some search"),  # Button text
    Const("order")  # Additinal text to search
)
