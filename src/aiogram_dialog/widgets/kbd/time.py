from collections.abc import Awaitable, Callable
from datetime import time

from aiogram.types import CallbackQuery, InlineKeyboardButton

from aiogram_dialog import ChatEvent, DialogManager, DialogProtocol
from aiogram_dialog.api.internal import RawKeyboard, StyleWidget, TextWidget
from aiogram_dialog.widgets.common import ManagedWidget, WhenCondition
from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog.widgets.style import EMPTY_STYLE
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.widget_event import (
    WidgetEventProcessor,
    ensure_event_processor,
)

OnClick = Callable[
    [CallbackQuery, "ManagedTimeSelect", DialogManager],
    Awaitable,
]
OnClickVariant = OnClick | WidgetEventProcessor | None

OnValueChanged = Callable[
    [ChatEvent, "ManagedTimeSelect", DialogManager, time | None],
    Awaitable,
]
OnValueChangedVariant = OnValueChanged | WidgetEventProcessor | None

HOUR_TEXT = Const("Hour")
MINUTE_TEXT = Const("Minute")


class TimeSelect(Keyboard):
    def __init__(
        self,
        id: str,
        when: WhenCondition = None,
        hour_header: TextWidget = HOUR_TEXT,
        minute_header: TextWidget = MINUTE_TEXT,
        header_style: StyleWidget = EMPTY_STYLE,
        selected_style: StyleWidget = EMPTY_STYLE,
        on_click: OnClickVariant = None,
        on_value_changed: OnValueChangedVariant = None,
        hour_width: int = 6,
        minute_precision: int = 5,
        minute_width: int = 6,
    ):
        super().__init__(id, when)
        self.hour_header = hour_header
        self.minute_header = minute_header
        self.header_style = header_style
        self.selected_style = selected_style
        self.minute_precision = minute_precision
        self.minute_width = minute_width
        self.hour_width = hour_width
        self.on_click = ensure_event_processor(on_click)
        self.on_value_changed = ensure_event_processor(on_value_changed)

    def _value_from_raw(
        self,
        raw_value: tuple[int | None, int | None],
    ) -> time | None:
        if None in raw_value:
            return None
        return time(raw_value[0], raw_value[1])

    def get_value(self, manager: DialogManager) -> time | None:
        raw_value = self.get_widget_data(manager, (None, None))
        return self._value_from_raw(raw_value)

    async def set_value(
        self,
        event: ChatEvent,
        manager: DialogManager,
        value: time | None,
    ) -> None:
        if value is None:
            self.set_widget_data(manager, [None, None])
        else:
            self.set_widget_data(manager, [value.hour, value.minute])
        await self.on_value_changed.process_event(
            event,
            self.managed(manager),
            manager,
            value,
        )

    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> RawKeyboard:
        rows = []
        old_hour, old_minute = self.get_widget_data(manager, (None, None))
        header_style = await self.header_style.render_style(data, manager)
        header_icon = await self.header_style.render_emoji(data, manager)
        selected_style = await self.selected_style.render_style(data, manager)
        selected_icon = await self.selected_style.render_emoji(data, manager)

        rows.append(
            [
                InlineKeyboardButton(
                    text=await self.hour_header.render_text(data, manager),
                    callback_data=self._own_callback_data(),
                    style=header_style,
                    icon_custom_emoji_id=header_icon,
                ),
            ],
        )
        for hour_row in self._rows(0, 24, 1, self.hour_width):
            row: list[InlineKeyboardButton] = []
            for hour in hour_row:
                is_selected = old_hour == hour
                row.append(
                    InlineKeyboardButton(
                        text=f"[{hour}]" if is_selected else f"{hour}",
                        callback_data=self._item_callback_data(f"h{hour}"),
                        style=(selected_style if is_selected else None),
                        icon_custom_emoji_id=(
                            selected_icon if is_selected else None
                        ),
                    ),
                )
            rows.append(row)

        rows.append(
            [
                InlineKeyboardButton(
                    text=await self.minute_header.render_text(data, manager),
                    callback_data=self._own_callback_data(),
                    style=header_style,
                    icon_custom_emoji_id=header_icon,
                ),
            ],
        )

        for minute_row in self._rows(
            0,
            60,
            self.minute_precision,
            self.minute_width,
        ):
            row = []
            for minute in minute_row:
                is_selected = old_minute == minute
                row.append(
                    InlineKeyboardButton(
                        text=f"[{minute}]" if is_selected else f"{minute}",
                        callback_data=self._item_callback_data(f"m{minute}"),
                        style=(selected_style if is_selected else None),
                        icon_custom_emoji_id=(
                            selected_icon if is_selected else None
                        ),
                    ),
                )
            rows.append(row)
        return rows

    def _rows(self, start, stop, step, width) -> list[list[int]]:
        rows = [[]]
        for i in range(start, stop, step):
            if len(rows[-1]) >= width:
                rows.append([])
            rows[-1].append(i)
        return rows

    async def _process_item_callback(
        self,
        callback: CallbackQuery,
        data: str,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        await self.on_click.process_event(
            manager.event,
            self.managed(manager),
            manager,
        )
        hour, minute = self.get_widget_data(manager, (None, None))
        if data.startswith("h"):
            hour = int(data[1:])
        elif data.startswith("m"):
            minute = int(data[1:])
        else:
            raise ValueError(f"Unknown callback format {data!r}")
        self.set_widget_data(manager, (hour, minute))
        value = self._value_from_raw((hour, minute))
        await self.on_value_changed.process_event(
            manager.event,
            self.managed(manager),
            manager,
            value,
        )
        return await super()._process_item_callback(
            callback,
            data,
            dialog,
            manager,
        )

    def managed(self, manager: DialogManager) -> "ManagedTimeSelect":
        return ManagedTimeSelect(self, manager)


class ManagedTimeSelect(ManagedWidget[TimeSelect]):
    def get_value(self) -> time | None:
        return self.widget.get_value(self.manager)

    async def set_value(self, value: time | None) -> None:
        return await self.widget.set_value(
            self.manager.event,
            self.manager,
            value,
        )
