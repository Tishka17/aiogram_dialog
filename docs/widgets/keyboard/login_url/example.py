from aiogram_dialog.widgets.kbd import LoginURLButton
from aiogram_dialog.widgets.text import Const

login_btn = LoginURLButton(
    text=Const("Login"),
    url=Const("https://example.com/login"),
    request_write_access=True,
)
