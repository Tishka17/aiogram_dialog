async def set_edit_show_mode(_, __, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.EDIT


Window(Progress(...), MessageInput(set_edit_show_mode), ...)
