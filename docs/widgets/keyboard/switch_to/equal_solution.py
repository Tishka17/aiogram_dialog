from aiogram_dialog.widgets.kbd import Button, SwitchTo

async def on_click(
        cq: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    ...  # your actions

button = SwitchTo(..., state=SOME_STATE, on_click=on_click)