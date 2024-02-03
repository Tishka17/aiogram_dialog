async def start_bg(callback: CallbackQuery, button: Button,
                   manager: DialogManager):
    bg = manager.bg(
        user_id=callback.from_user.id,
        chat_id=callback.message.chat.id,
        stack_id="progress_stack",
        load=True,
    )
    await bg.start(Bg.progress)
    asyncio.create_task(background(callback, bg))