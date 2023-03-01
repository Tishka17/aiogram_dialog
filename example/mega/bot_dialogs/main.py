from aiogram_dialog import (
    Dialog, Window, LaunchMode,
)
from aiogram_dialog.widgets.kbd import (
    Start,
)
from aiogram_dialog.widgets.text import Const
from . import states

main_dialog = Dialog(
    Window(
        Const("This is aiogram-dialog demo application"),
        Const("Use buttons below to see some options."),
        Start(
            text=Const("📐 Layout widgets"),
            id="scrolls",
            state=states.Layouts.MAIN,
        ),
        Start(
            text=Const("📜 Scrolling widgets"),
            id="scrolls",
            state=states.Scrolls.MAIN,
        ),
        Start(
            text=Const("📅 Calendar"),
            id="cal",
            state=states.Calendar.MAIN,
        ),
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
