from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from typing import Dict

from aiogram import Bot
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, User

from .intent import Intent, DialogUpdateEvent, DialogStartEvent, Action, DialogSwitchEvent
from .manager import DialogManager

logger = getLogger(__name__)


def handle_update(event: DialogUpdateEvent, dialog_manager: DialogManager):
    if dialog_manager.current_intent() != event.current_intent:
        logger.info("Current intent changed, skipping update processing")
        return

    if isinstance(event, DialogStartEvent):
        await dialog_manager.start(state=event.new_state, data=event.data, reset_stack=event.reset_stack)
    elif isinstance(event, DialogSwitchEvent):
        await dialog_manager.switch_to(state=event.new_state)
        await dialog_manager.dialog().show(dialog_manager)
    elif event.action is Action.UPDATE:
        await dialog_manager.dialog().show(dialog_manager)
    elif event.action is Action.DONE:
        dialog_manager.done(result=event.data)