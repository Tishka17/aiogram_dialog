async def open_next_window(event, widget, manager: DialogManager):
    manager.show_mode = ShowMode.SEND
    await manager.next()


async def switch_to_another_window(event, widget, manager: DialogManager):
    await manager.switch_to(
        state=SomeStatesSG.SomeState,
        show_mode=ShowMode.SEND,
    )
