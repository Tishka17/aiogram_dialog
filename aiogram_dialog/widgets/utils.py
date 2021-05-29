from typing import Union, Sequence, Tuple, Callable

from .input import MessageHandlerFunc, BaseInput, MessageInput
from .kbd import Keyboard, Group
from .text import Multi, Format, Text
from .widget_event import WidgetEventProcessor
from ..exceptions import InvalidWidgetType, InvalidWidget


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


def ensure_input(
        widget: Union[MessageHandlerFunc, WidgetEventProcessor, BaseInput, Sequence[BaseInput]]
) -> BaseInput:
    if isinstance(widget, BaseInput):
        return widget
    elif isinstance(widget, Sequence):
        if len(widget) == 0:
            return MessageInput(None)
        elif len(widget) == 1:
            return widget[0]
        else:
            raise InvalidWidget(f"Only 1 input supported, got {len(widget)}")
    else:
        return MessageInput(widget)


def ensure_widgets(
        widgets: Sequence[Union[str, Text, Keyboard, MessageHandlerFunc, BaseInput]]
) -> Tuple[Text, Keyboard, BaseInput]:
    texts = []
    keyboards = []
    inputs = []

    for w in widgets:
        if isinstance(w, (str, Text)):
            texts.append(ensure_text(w))
        elif isinstance(w, Keyboard):
            keyboards.append(ensure_keyboard(w))
        elif isinstance(w, (BaseInput, Callable)):
            inputs.append(ensure_input(w))
        else:
            raise InvalidWidgetType(
                f"Cannot add widget of type {type(w)}. "
                f"Only str, Text, Keyboard, BaseInput and Callable are supported"
            )
    return ensure_text(texts), ensure_keyboard(keyboards), ensure_input(inputs)
