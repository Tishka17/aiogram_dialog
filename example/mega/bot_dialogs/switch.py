from typing import Any, Dict

from aiogram_dialog import (
    Dialog, Window, DialogManager,
)
from aiogram_dialog.widgets.kbd import Next, Row, Back, Checkbox, Radio
from aiogram_dialog.widgets.text import Const, Format, Case
from . import states
from .common import MAIN_MENU_BUTTON

HEADER = Const("Multiple windows in the same dialog can be used "
               "to provide step by step user data input.\n")
CHECKBOX_ID = "chk"
EMOJI_ID = "emoji"

main_window = Window(
    HEADER,
    Const("Step 1. Press Next"),
    Next(),
    MAIN_MENU_BUTTON,
    state=states.Switch.MAIN,
)
input_window = Window(
    HEADER,
    Const("Step 2. Select options"),
    Checkbox(
        Const("✓ Option is enabled"),
        Const("Click to enable the option"),
        id=CHECKBOX_ID,
    ),
    Radio(
        checked_text=Format("🔘 {item}"),
        unchecked_text=Format("⚪️ {item}"),
        items=["😆", "😱", "😈", "🤖", "🤡"],
        item_id_getter=lambda x: x,
        id=EMOJI_ID,
    ),
    Row(Back(), Next()),
    MAIN_MENU_BUTTON,
    state=states.Switch.INPUT,
)


async def data_getter(
        dialog_manager: DialogManager, **_kwargs,
) -> Dict[str, Any]:
    return {
        "option": dialog_manager.find(CHECKBOX_ID).is_checked(),
        "emoji": dialog_manager.find(EMOJI_ID).get_checked(),
    }


last_window = Window(
    HEADER,
    Const("Step 3. Your data:"),
    Case(
        {
            True: Const("Option: enabled"),
            False: Const("Option: disabled"),
        },
        selector="option",
    ),
    Format("Selected emoji: {emoji}"),
    Back(),
    MAIN_MENU_BUTTON,
    state=states.Switch.LAST,
    getter=data_getter,
)
switch_dialog = Dialog(
    main_window,
    input_window,
    last_window,
)
