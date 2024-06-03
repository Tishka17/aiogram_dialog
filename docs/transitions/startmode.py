async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(..., mode=StartMode.RESET_STACK)
