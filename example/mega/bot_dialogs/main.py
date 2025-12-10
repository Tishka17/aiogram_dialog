from aiogram_dialog import Dialog, LaunchMode, Window
from aiogram_dialog.about import about_aiogram_dialog_button
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const
from . import states

main_dialog = Dialog(
    Window(
        Const("This is aiogram-dialog demo application"),
        Const("Use buttons below to see some options."),
        Start(
            text=Const("📐 Layout widgets"),
            id="layout",
            state=states.Layouts.MAIN,
        ),
        Start(
            text=Const("📜 Scrolling widgets"),
            id="scrolls",
            state=states.Scrolls.MAIN,
        ),
        Start(
            text=Const("☑️ Selection widgets"),
            id="selects",
            state=states.Selects.MAIN,
        ),
        Start(
            text=Const("📅 Calendar"),
            id="cal",
            state=states.Calendar.MAIN,
        ),
        Start(
            text=Const("💯 Counter and Progress"),
            id="counter",
            state=states.Counter.MAIN,
        ),
        Start(
            text=Const("🎛 Combining widgets"),
            id="multiwidget",
            state=states.Multiwidget.MAIN,
        ),
        Start(
            text=Const("🔢 Multiple steps"),
            id="switch",
            state=states.Switch.MAIN,
        ),
        Start(
            text=Const("🔗 Link Preview"),
            id="linkpreview",
            state=states.LinkPreview.MAIN,
        ),
        Start(
            text=Const("⌨️ Reply keyboard"),
            id="reply",
            state=states.ReplyKeyboard.MAIN,
        ),
        about_aiogram_dialog_button(),
        state=states.Main.MAIN,
    ),
    launch_mode=LaunchMode.ROOT,
)
