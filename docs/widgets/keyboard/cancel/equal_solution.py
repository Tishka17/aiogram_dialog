from aiogram_dialog.widgets.kbd import Button, Cancel

async def on_click(
        cq: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    ...  # your actions

button = Cancel(..., on_click=on_click)