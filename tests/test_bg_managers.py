import pytest
from aiogram import Dispatcher
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, Window, setup_dialogs
from aiogram_dialog.manager.fg_manager import FgManagerFactoryImpl
from aiogram_dialog.test_tools.bot_client import FakeBot
from aiogram_dialog.widgets.text import Const


class SomeStates(StatesGroup):
    some = State()


@pytest.mark.asyncio
async def test_bg_manager_running_without_waiting() -> None:
    bot = FakeBot()
    dp = Dispatcher()
    some_dialog = Dialog(Window(Const("Text"), state=SomeStates.some))

    dp.include_routers(some_dialog)
    bg_manager_factory = setup_dialogs(dp)
    bg_manager = bg_manager_factory.bg(bot=bot, user_id=1, chat_id=1)

    # No RuntimeError, because BgManager schedules the dialog start
    # in the background and does not await it
    await bg_manager.start(state=SomeStates.some)


@pytest.mark.asyncio
async def test_fg_manager_running_with_waiting() -> None:
    bot = FakeBot()
    dp = Dispatcher()
    some_dialog = Dialog(Window(Const("Text"), state=SomeStates.some))

    dp.include_routers(some_dialog)
    bg_manager_factory = setup_dialogs(
        dp,
        bg_manager_factory=FgManagerFactoryImpl(dp),
    )
    bg_manager = bg_manager_factory.bg(bot=bot, user_id=1, chat_id=1)

    # Raises RuntimeError, because FgManager awaits the dialog start,
    # triggering a FakeBot Telegram API call.
    with pytest.raises(
        RuntimeError,
        match="Fake bot should not be used to call telegram",
    ):
        await bg_manager.start(state=SomeStates.some)
