from aiogram_dialog import DialogManager, ChatEvent
from aiogram_dialog.widgets.kbd import Checkbox, ManagedCheckboxAdapter
from aiogram_dialog.widgets.text import Const


async def check_changed(event: ChatEvent, checkbox: ManagedCheckboxAdapter,
                        manager: DialogManager):
    print("Check status changed:", checkbox.is_checked())


check = Checkbox(
    Const("✓  Checked"),
    Const("Unchecked"),
    id="check",
    default=True,  # so it will be checked by default,
    on_state_changed=check_changed,
)
