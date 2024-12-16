from aiogram_dialog import (
    Dialog,
    Window,
)
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.link_preview import LinkPreview
from aiogram_dialog.widgets.text import Const, Format
from . import states
from .common import MAIN_MENU_BUTTON


async def links_getter(**_):
    return {
        "main": "https://en.wikipedia.org/wiki/HTML_element",
        "photo": "https://en.wikipedia.org/wiki/Hyperlink",
    }


LinkPreview_MAIN_MENU_BUTTON = SwitchTo(
    text=Const("Back"), id="back", state=states.LinkPreview.MAIN,
)
COMMON_TEXT = Format(
    "This is demo of different link preview options.\n"
    "Link in text: {main}\n"
    "Link in preview can be different\n\n"
    "Current mode is:",
)

BACK = SwitchTo(Const("back"), "_back", states.LinkPreview.MAIN)

link_preview_dialog = Dialog(
    Window(
        COMMON_TEXT,
        Format("Default"),
        SwitchTo(
            Const("disable"), "_disable", states.LinkPreview.IS_DISABLED,
        ),
        SwitchTo(
            Const("prefer small media"), "_prefer_small_media",
            states.LinkPreview.SMALL_MEDIA,
        ),
        SwitchTo(
            Const("prefer large media"), "_prefer_large_media",
            states.LinkPreview.LARGE_MEDIA,
        ),
        SwitchTo(
            Const("show above text"), "_show_above_text",
            states.LinkPreview.SHOW_ABOVE_TEXT,
        ),
        MAIN_MENU_BUTTON,
        state=states.LinkPreview.MAIN,
    ),
    Window(
        COMMON_TEXT,
        Const("is_disabled=True"),
        LinkPreview(is_disabled=True),
        LinkPreview_MAIN_MENU_BUTTON,
        state=states.LinkPreview.IS_DISABLED,
    ),
    Window(
        COMMON_TEXT,
        Const("prefer_small_media=True"),
        LinkPreview(Format("{photo}"), prefer_small_media=True),
        LinkPreview_MAIN_MENU_BUTTON,
        state=states.LinkPreview.SMALL_MEDIA,
    ),
    Window(
        COMMON_TEXT,
        Const("prefer_large_media=True"),
        LinkPreview(Format("{photo}"), prefer_large_media=True),
        LinkPreview_MAIN_MENU_BUTTON,
        state=states.LinkPreview.LARGE_MEDIA,
    ),
    Window(
        COMMON_TEXT,
        Const("show_above_text=True"),
        LinkPreview(Format("{photo}"), show_above_text=True),
        LinkPreview_MAIN_MENU_BUTTON,
        state=states.LinkPreview.SHOW_ABOVE_TEXT,
    ),
    getter=links_getter,
)
