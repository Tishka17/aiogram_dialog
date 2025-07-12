from collections.abc import Awaitable, Callable
from typing import Any, Final, Union, cast

from aiogram import Router
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject

from aiogram_dialog.api.entities import ChatEvent, DialogUpdateEvent
from aiogram_dialog.api.internal import STORAGE_KEY, DialogManagerFactory
from aiogram_dialog.api.protocols import (
    BgManagerFactory,
    DialogManager,
    DialogRegistryProtocol,
)

MANAGER_KEY: Final = "dialog_manager"
BG_FACTORY_KEY: Final = "dialog_bg_factory"


class ManagerMiddleware(BaseMiddleware):
    def __init__(
            self,
            dialog_manager_factory: DialogManagerFactory,
            registry: DialogRegistryProtocol,
            router: Router,
    ) -> None:
        self.dialog_manager_factory = dialog_manager_factory
        self.registry = registry
        self.router = router

    def _is_event_supported(
            self, event: TelegramObject, data: dict[str, Any],
    ) -> bool:
        return STORAGE_KEY in data

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, dict[str, Any]],
                Awaitable[Any],
            ],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        if self._is_event_supported(event, data):
            data[MANAGER_KEY] = self.dialog_manager_factory(
                event=cast(ChatEvent, event),
                data=data,
                registry=self.registry,
                router=self.router,
            )

        try:
            return await handler(event, data)
        finally:
            manager: DialogManager = data.pop(MANAGER_KEY, None)
            if manager:
                await manager.close_manager()


class BgFactoryMiddleware(BaseMiddleware):
    def __init__(
            self,
            bg_manager_factory: BgManagerFactory,
    ) -> None:
        self.bg_manager_factory = bg_manager_factory

    async def __call__(
            self,
            handler: Callable[
                [Union[TelegramObject, DialogUpdateEvent], dict[str, Any]],
                Awaitable[TelegramObject],
            ],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        data[BG_FACTORY_KEY] = self.bg_manager_factory
        return await handler(event, data)
