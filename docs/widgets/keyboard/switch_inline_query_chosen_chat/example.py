from aiogram_dialog.widgets.kbd import SwitchInlineQueryChosenChatButton
from aiogram_dialog.widgets.text import Const

switch_btn = SwitchInlineQueryChosenChatButton(
    text=Const("Send inline query in the chosen chat"),
    query=Const("inline query in the chosen chat"),
    allow_user_chats=True,
    allow_group_chats=True,
    allow_channel_chats=False,
)
