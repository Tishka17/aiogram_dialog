from aiogram_dialog.widgets.kbd import SwitchInlineQueryCurrentChat
from aiogram_dialog.widgets.text import Const

switch_btn = SwitchInlineQueryCurrentChat(
    text=Const("Send inline query in the current chat"),
    switch_inline_query_current_chat=Const("inline query in the current chat"),
)
