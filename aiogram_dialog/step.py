from typing import Tuple, Optional, Any, Sequence

from aiogram.dispatcher.filters.state import State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery


class Step:
    def __init__(
            self,
            prompt: str = "",
            can_cancel: bool = True,
            can_back: bool = True,
            can_done: bool = True,
            can_skip: bool = True,
            field: Optional[str] = None,
            back: State = NotImplemented,
            next: State = NotImplemented
    ):
        self._can_cancel = can_cancel
        self._can_back = can_back
        self._can_done = can_done
        self._can_skip = can_skip
        self._field = field
        self.prompt = prompt
        if back and back is not NotImplemented:
            back: str = back.state
        self.back = back
        if next and next is not NotImplemented:
            next = next.state
        self.next: str = next

    def can_cancel(self) -> bool:
        return self._can_cancel

    def can_back(self) -> bool:
        return self._can_back

    def can_done(self) -> bool:
        return self._can_done

    def can_skip(self) -> bool:
        return self._can_skip

    async def render_text(self, current_data, *args, **kwargs):
        return self.prompt

    async def render_kbd(self, current_data, *args, **kwargs) -> Optional[InlineKeyboardMarkup]:
        pass

    def field(self) -> Optional[str]:
        return self._field

    async def process_callback(self, callback: CallbackQuery, current_data,
                               *args, **kwargs) -> Tuple[Any, Optional[str]]:
        raise NotImplementedError

    async def process_message(self, message: Message, current_data,
                              *args, **kwargs) -> Tuple[Any, Optional[str]]:
        raise NotImplementedError


class DataStep(Step):
    def __init__(
            self,
            variants: Sequence[Tuple[str, Any]] = (),
            type_factory=str,
            allow_text: Optional[bool] = None,
            multiple: bool = False,
            checked_prefix: str = "\N{HEAVY CHECK MARK} ",
            unchecked_prefix: str = "",
            reorder_variants_by: int = 0,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.variants = variants
        self.type_factory = type_factory
        if allow_text is None:
            allow_text = not variants
        self.allow_text = allow_text
        self.multiple = multiple
        self.checked_prefix = checked_prefix
        self.unchecked_prefix = unchecked_prefix
        self.reorder_variants_by = reorder_variants_by

    async def process_callback(self, callback: CallbackQuery, current_data,
                               *args, **kwargs) -> Tuple[Any, Optional[str]]:
        value = self.type_factory(callback.data)
        if self.multiple:
            current_value = current_data.get(self.field(), [])
            filtered_value = [x for x in current_value if x != value]
            if filtered_value == current_value:
                return current_value + [value], self.next
            else:
                return filtered_value, self.next
        return value, self.next

    async def process_message(self, message: Message, current_data,
                              *args, **kwargs) -> Tuple[Any, Optional[str]]:
        if not self.allow_text:
            raise ValueError

        value = self.type_factory(message.text)
        if self.multiple:
            res = current_data.get(self.field(), [])
            return res + [value], self.next
        return value, self.next

    async def get_variants(self, current_data, *args, **kwargs):
        return self.variants

    async def render_kbd(self, current_data, *args, **kwargs) -> Optional[InlineKeyboardMarkup]:
        kbd = InlineKeyboardMarkup()
        variants = await self.get_variants(current_data, *args, **kwargs)
        field = self.field()
        row = []
        for title, data in variants:
            if self.multiple and field:
                if data in current_data.get(field, []):
                    title = self.checked_prefix + title
                else:
                    title = self.unchecked_prefix + title
            row.append(InlineKeyboardButton(title, callback_data=data))
            if not self.reorder_variants_by or len(row) >= self.reorder_variants_by:
                kbd.row(*row)
                row = []
        if row:
            kbd.row(*row)
        return kbd


class StateStep(DataStep):
    async def process_callback(self, callback: CallbackQuery, current_data,
                               *args, **kwargs) -> Tuple[Any, Optional[str]]:
        return callback.data, callback.data

    async def process_message(self, text, current_data,
                              *args, **kwargs) -> Tuple[Any, Optional[str]]:
        raise ValueError
