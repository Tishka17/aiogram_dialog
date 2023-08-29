from logging import getLogger
from typing import Any, Dict, Optional

from aiogram import Bot, Router
from aiogram.fsm.state import State
from aiogram.types import Chat, User

from aiogram_dialog.api.entities import (
    Data,
    DEFAULT_STACK_ID,
    DialogAction,
    DialogStartEvent,
    DialogSwitchEvent,
    DialogUpdate,
    DialogUpdateEvent,
    ShowMode,
    StartMode,
)
from aiogram_dialog.api.internal import (
    FakeChat, FakeUser,
)
from aiogram_dialog.api.protocols import BaseDialogManager, BgManagerFactory
from aiogram_dialog.manager.updater import Updater
from aiogram_dialog.utils import is_chat_loaded, is_user_loaded

logger = getLogger(__name__)


class BgManager(BaseDialogManager):
    def __init__(
            self,
            user: User,
            chat: Chat,
            bot: Bot,
            router: Router,
            intent_id: Optional[str],
            stack_id: Optional[str],
            load: bool = False,
    ):
        self.user = user
        self.chat = chat
        self.bot = bot
        self._router = router
        self._updater = Updater(router)
        self.intent_id = intent_id
        self.stack_id = stack_id
        self.load = load

    def bg(
            self,
            user_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            stack_id: Optional[str] = None,
            load: bool = False,
    ) -> "BaseDialogManager":
        if chat_id in (None, self.chat.id):
            chat = self.chat
        else:
            chat = FakeChat(id=chat_id, type="")

        if user_id in (None, self.user.id):
            user = self.user
        else:
            user = FakeUser(id=user_id, is_bot=False, first_name="")

        same_chat = user.id == self.user.id and chat.id == self.chat.id
        if stack_id is None:
            if same_chat:
                stack_id = self.stack_id
                intent_id = self.intent_id
            else:
                stack_id = DEFAULT_STACK_ID
                intent_id = None
        else:
            intent_id = None

        return BgManager(
            user=user,
            chat=chat,
            bot=self.bot,
            router=self._router,
            intent_id=intent_id,
            stack_id=stack_id,
            load=load,
        )

    def _base_event_params(self):
        return {
            "from_user": self.user,
            "chat": self.chat,
            "intent_id": self.intent_id,
            "stack_id": self.stack_id,
        }

    async def _notify(self, event: DialogUpdateEvent):
        await self._updater.notify(
            bot=self.bot, update=DialogUpdate(aiogd_update=event),
        )

    async def _load(self):
        if self.load:
            if not is_chat_loaded(self.chat):
                logger.debug("load chat: %s", self.chat.id)
                self.chat = await self.bot.get_chat(self.chat.id)
            if not is_user_loaded(self.user):
                logger.debug(
                    "load user %s from chat %s", self.chat.id, self.user.id,
                )
                chat_member = await self.bot.get_chat_member(
                    self.chat.id, self.user.id,
                )
                self.user = chat_member.user

    async def done(
            self,
            result: Any = None,
            show_mode: Optional[ShowMode] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogUpdateEvent(
                action=DialogAction.DONE, data=result, show_mode=show_mode,
                **self._base_event_params(),
            ),
        )

    async def start(
            self,
            state: State,
            data: Data = None,
            mode: StartMode = StartMode.NORMAL,
            show_mode: Optional[ShowMode] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogStartEvent(
                action=DialogAction.START,
                data=data,
                new_state=state,
                mode=mode,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )

    async def switch_to(
            self,
            state: State,
            show_mode: Optional[ShowMode] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogSwitchEvent(
                action=DialogAction.SWITCH,
                data={},
                new_state=state,
                show_mode=show_mode,
                **self._base_event_params(),
            ),
        )

    async def update(
            self,
            data: Dict,
            show_mode: Optional[ShowMode] = None,
    ) -> None:
        await self._load()
        await self._notify(
            DialogUpdateEvent(
                action=DialogAction.UPDATE, data=data, show_mode=show_mode,
                **self._base_event_params(),
            ),
        )


class BgManagerFactoryImpl(BgManagerFactory):
    def __init__(self, router: Router):
        self._router = router

    def bg(
            self,
            bot: Bot,
            user_id: int,
            chat_id: int,
            stack_id: Optional[str] = None,
            load: bool = False,
    ) -> "BaseDialogManager":
        chat = FakeChat(id=chat_id, type="")
        user = FakeUser(id=user_id, is_bot=False, first_name="")
        if stack_id is None:
            stack_id = DEFAULT_STACK_ID

        return BgManager(
            user=user,
            chat=chat,
            bot=bot,
            router=self._router,
            intent_id=None,
            stack_id=stack_id,
            load=load,
        )
