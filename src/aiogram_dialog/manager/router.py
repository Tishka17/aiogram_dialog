from functools import partial
from typing import Optional, Type, Dict, Any

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.fsm.state import any_state, StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import (
    BaseDialogManager, DEFAULT_STACK_ID, DialogProtocol, DialogManager,
    StartMode,
)
from aiogram_dialog.api.exceptions import UnregisteredDialogError
from aiogram_dialog.api.internal import FakeUser, FakeChat
from aiogram_dialog.api.protocols import DialogRegistryProtocol
from aiogram_dialog.context.intent_filter import IntentFilter
from aiogram_dialog.manager.bg_manager import BgManager
from aiogram_dialog.manager.updater import Updater


class DialogRouter(Router, DialogRegistryProtocol):
    def __init__(self, *, name: Optional[str] = None) -> None:
        super().__init__(name=name)
        self.dialogs: Dict[Type[StatesGroup], DialogProtocol] = {}

    def state_groups(self) -> Dict[str, Type[StatesGroup]]:
        return {
            d.states_group_name(): d.states_group()
            for d in self.dialogs.values()
        }

    def find_dialog(self, state: State) -> DialogProtocol:
        try:
            return self.dialogs[state.group]
        except KeyError as e:
            raise UnregisteredDialogError(
                f"No dialog found for `{state.group}`"
                f" (looking by state `{state}`)",
            ) from e

    def _register(
            self,
            dialog: Optional[DialogProtocol],
            args,
            kwargs,
    ):
        self.dialogs[dialog.states_group()] = dialog
        return dialog.register(
            self,
            IntentFilter(aiogd_intent_state_group=dialog.states_group()),
            *args,
            **kwargs,
        )

    def register(
            self,
            dialog: Optional[DialogProtocol] = None,
            *args,
            **kwargs,
    ) -> Any:
        if dialog is not None:
            return self._register(dialog, args, kwargs)

        else:
            return partial(self._register, args=args, kwargs=kwargs)

    def _extend_dialogs(self, router: "DialogRouter") -> None:
        for group, dialog in router.dialogs.items():
            self.dialogs[group] = dialog

    def include_router(self, router: Router) -> Router:
        if isinstance(router, DialogRouter):
            self._extend_dialogs(router)
        return super().include_router(router)

    def register_start_handler(self, state: State):
        async def start_dialog(
                message: Message, dialog_manager: DialogManager,
        ) -> None:
            await dialog_manager.start(state, mode=StartMode.RESET_STACK)

        self.message.register(
            start_dialog, Command(commands="start"), any_state,
        )

    def bg(
            self,
            dp: Router,
            bot: Bot,
            user_id: int,
            chat_id: int,
            stack_id: str = DEFAULT_STACK_ID,
            intent_id: Optional[str] = None,
            load: bool = False,
    ) -> BaseDialogManager:
        return BgManager(
            user=FakeUser(id=user_id, is_bot=False, first_name=""),
            chat=FakeChat(id=chat_id, type=""),
            bot=bot,
            updater=Updater(dp),
            intent_id=intent_id,
            stack_id=stack_id,
            load=load,
        )
