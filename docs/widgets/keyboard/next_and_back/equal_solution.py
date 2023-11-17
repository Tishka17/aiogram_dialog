from aiogram_dialog.widgets.kbd import Button, Next  # or Back

async def on_click(
        cq: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    ...  # your actions

button = Next(..., on_click=on_click)  # or Back