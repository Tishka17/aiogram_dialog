from typing import Callable, Dict, Union

from magic_filter import MagicFilter

from aiogram_dialog.api.protocols import DialogManager

Predicate = Callable[[Dict, "Whenable", DialogManager], bool]
WhenCondition = Union[str, MagicFilter, Predicate, None]


def new_when_field(fieldname: str) -> Predicate:
    def when_field(
            data: Dict, widget: "Whenable", manager: DialogManager,
    ) -> bool:
        return bool(data.get(fieldname))

    return when_field


def new_when_magic(f: MagicFilter) -> Predicate:
    def when_magic(
            data: Dict, widget: "Whenable", manager: DialogManager,
    ) -> bool:
        return f.resolve(data)

    return when_magic


def true_condition(data: Dict, widget: "Whenable", manager: DialogManager):
    return True


class Whenable:
    def __init__(self, when: WhenCondition = None):
        self.condition: Predicate
        if when is None:
            self.condition = true_condition
        elif isinstance(when, str):
            self.condition = new_when_field(when)
        elif isinstance(when, MagicFilter):
            self.condition = new_when_magic(when)
        else:
            self.condition = when

    def is_(self, data: Dict, manager: DialogManager):
        return self.condition(data, self, manager)
