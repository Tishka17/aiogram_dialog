from typing import Union, Callable, Dict

from dialog.manager.manager import DialogManager

Predicate = Callable[[Dict, "Whenable", DialogManager], bool]
WhenCondition = Union[str, Predicate, None]


def new_when_field(fieldname: str) -> Predicate:
    def when_field(data: Dict, widget: "Whenable", manager: DialogManager) -> bool:
        return data.get(fieldname)

    return when_field


def true(data: Dict, widget: "Whenable", manager: DialogManager):
    return True


class Whenable():
    condition: Predicate

    def __init__(self, when: WhenCondition = None):
        if when is None:
            self.condition = true
        if isinstance(when, str):
            self.condition = new_when_field(when)
        else:
            self.condition = when

    def is_(self, data, manager):
        return self.condition(data, self, manager)
