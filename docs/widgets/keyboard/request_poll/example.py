from aiogram_dialog.widgets.kbd import RequestPoll
from aiogram_dialog.widgets.text import Const

# Regular poll
poll_btn = RequestPoll(
    text=Const("Create Poll"),
)

# Quiz poll
quiz_btn = RequestPoll(
    text=Const("Create Quiz"),
    poll_type="quiz",
)
