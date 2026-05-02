from aiogram_dialog.widgets.kbd import CopyText
from aiogram_dialog.widgets.text import Const, Format

copy_btn = CopyText(
    text=Const("Copy name"),
    copy_text=Const("Tishka17"),
)

copy_dynamic_btn = CopyText(
    text=Const("Copy ID"),
    copy_text=Format("{user_id}"),
)
