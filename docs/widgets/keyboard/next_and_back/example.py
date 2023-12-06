from aiogram_dialog.widgets.kbd import Button

async def on_click(
        cq: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    ...  # your actions
    await dialog_manager.next()

button = Button(..., on_click=on_click)