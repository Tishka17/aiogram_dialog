from typing import Optional

from aiogram import Bot, Router
from aiogram.types import Chat, User

from aiogram_dialog.api.entities import DEFAULT_STACK_ID

from aiogram_dialog.api.internal import FakeChat, FakeUser
from aiogram_dialog.api.protocols import BaseDialogManager
from aiogram_dialog.manager.bg_manager import BgManager, BgManagerFactoryImpl
from aiogram_dialog.manager.simple_updater import SimpleUpdater


class FgManager(BgManager):
    def __init__(
        self,
        user: User,
        chat: Chat,
        bot: Bot,
        router: Router,
        intent_id: Optional[str],
        stack_id: Optional[str],
        thread_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        load: bool = False,
    ):
        super().__init__(
            user=user,
            chat=chat,
            bot=bot,
            router=router,
            intent_id=intent_id,
            stack_id=stack_id,
            thread_id=thread_id,
            business_connection_id=business_connection_id,
            load=load,
        )
        self._updater = SimpleUpdater(router)


class FgManagerFactoryImpl(BgManagerFactoryImpl):
    def bg(
        self,
        bot: Bot,
        user_id: int,
        chat_id: int,
        stack_id: Optional[str] = None,
        thread_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        load: bool = False,
    ) -> "BaseDialogManager":
        chat = FakeChat(id=chat_id, type="")
        user = FakeUser(id=user_id, is_bot=False, first_name="")
        if stack_id is None:
            stack_id = DEFAULT_STACK_ID

        return FgManager(
            user=user,
            chat=chat,
            bot=bot,
            router=self._router,
            intent_id=None,
            stack_id=stack_id,
            thread_id=thread_id,
            business_connection_id=business_connection_id,
            load=load,
        )
