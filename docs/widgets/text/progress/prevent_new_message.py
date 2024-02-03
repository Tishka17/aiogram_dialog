async def set_edit_show_mode(_, __, dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.EDIT


Window(
    Multi(
        Const("Your click is processing, please wait..."),
        Progress("progress", 10),
    ),
    MessageInput(set_edit_show_mode),
    state=Main.progress,
    getter=get_bg_data,
),