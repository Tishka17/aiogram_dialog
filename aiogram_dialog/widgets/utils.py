from typing import Union, Sequence, Tuple, Callable, Dict, List

from .data.data_context import DataGetter, StaticGetter, CompositeGetter
from .input import MessageHandlerFunc, BaseInput, MessageInput
from .kbd import Keyboard, Group
from .media import Media
from .text import Multi, Format, Text
from .widget_event import WidgetEventProcessor
from ..exceptions import InvalidWidgetType, InvalidWidget

WidgetSrc = Union[str, Text, Keyboard, MessageHandlerFunc, Media, BaseInput]

SingleGetterBase = Union[DataGetter, Dict]
GetterVariant = Union[
    None, SingleGetterBase,
    List[SingleGetterBase], Tuple[SingleGetterBase, ...],
]


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
        widget: Union[
            MessageHandlerFunc, WidgetEventProcessor, BaseInput,
            Sequence[BaseInput]
        ]
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


def ensure_media(widget: Union[Media, Sequence[Media]]) -> Media:
    if isinstance(widget, Media):
        return widget
    if len(widget) > 1:  # TODO case selection of media
        raise ValueError("Only one media widget is supported")
    if len(widget) == 1:
        return widget[0]
    return Media()


def ensure_widgets(
        widgets: Sequence[WidgetSrc]
) -> Tuple[Text, Keyboard, BaseInput, Media]:
    texts = []
    keyboards = []
    inputs = []
    media = []

    for w in widgets:
        if isinstance(w, (str, Text)):
            texts.append(ensure_text(w))
        elif isinstance(w, Keyboard):
            keyboards.append(ensure_keyboard(w))
        elif isinstance(w, (BaseInput, Callable)):
            inputs.append(ensure_input(w))
        elif isinstance(w, Media):
            media.append(ensure_media(w))
        else:
            raise InvalidWidgetType(
                f"Cannot add widget of type {type(w)}. "
                f"Only str, Text, Keyboard, BaseInput and Callable are supported"
            )
    return (
        ensure_text(texts),
        ensure_keyboard(keyboards),
        ensure_input(inputs),
        ensure_media(media),
    )


def ensure_data_getter(getter: GetterVariant) -> DataGetter:
    if isinstance(getter, Callable):
        return getter
    elif isinstance(getter, dict):
        return StaticGetter(getter)
    elif isinstance(getter, (list, tuple)):
        return CompositeGetter(*map(ensure_data_getter, getter))
    elif getter is None:
        return StaticGetter({})
    else:
        raise InvalidWidgetType(
            f"Cannot add data getter of type {type(getter)}. "
            f"Only Dict, Callable or List of Callables are supported"
        )
