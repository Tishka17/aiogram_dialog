from typing import Union, Sequence, Tuple

from .kbd import Keyboard, Group
from .text import Multi, Format, Text


def ensure_text(widget: Union[str, Text, Sequence[Text]]) -> Text:
    if isinstance(widget, str):
        return Format(widget)
    if isinstance(widget, Sequence):
        if len(widget) == 1:
            return widget[0]
        return Multi(*widget)
    return widget


def ensure_keyboard(widget: Union[Keyboard, Sequence[Keyboard]]) -> Keyboard:
    if isinstance(widget, Sequence):
        if len(widget) == 1:
            return widget[0]
        return Group(*widget)
    return widget


def ensure_widgets(widgets: Sequence[Union[str, Text, Keyboard]]) -> Tuple[Text, Keyboard]:
    texts = []
    keyboards = []

    for w in widgets:
        if isinstance(w, (str, Text)):
            texts.append(ensure_text(w))
        elif isinstance(w, Keyboard):
            keyboards.append(ensure_keyboard(w))
        else:
            raise TypeError("Invalid widget type: %s" % type(w))
    return ensure_text(texts), ensure_keyboard(keyboards)
