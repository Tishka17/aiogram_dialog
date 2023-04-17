from aiogram_dialog import (
    Dialog, Window, DialogManager, )
from aiogram_dialog.widgets.kbd import (
    Counter, ManagedCounterAdapter,
)
from aiogram_dialog.widgets.text import Const, Progress
from . import states
from .common import MAIN_MENU_BUTTON

ID_COUNTER = "counter"
MAX_VALUE = 10
FIELD_PROGRESS = "progress"


async def getter(dialog_manager: DialogManager, **kwargs):
    counter: ManagedCounterAdapter = dialog_manager.find(ID_COUNTER)
    return {
        FIELD_PROGRESS: counter.get_value() / MAX_VALUE * 100,
    }


counter_dialog = Dialog(
    Window(
        Const("`Counter` widget is used to create +/- buttons."),
        Const("`Progress` widget shows percentage\n"),
        Progress(field=FIELD_PROGRESS),
        Counter(
            id=ID_COUNTER,
            default=0,
            max_value=MAX_VALUE,
        ),
        MAIN_MENU_BUTTON,
        state=states.Counter.MAIN,
        getter=getter,
    ),
)
