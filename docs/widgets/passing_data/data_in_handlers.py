async def button1_clicked(callback: CallbackQuery, button: Button, manager: DialogManager):
    dialog_data = manager.dialog_data
    event = manager.event
    middleware_data = manager.middleware_data
    start_data = manager.start_data