from aiogram_dialog.widgets.kbd import Button, Start

async def on_click(
        cq: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    ...  # your actions

button = Start(..., state=SOME_STATE, data=SOME_DATA, on_click=on_click)