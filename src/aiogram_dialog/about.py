import importlib.metadata

from aiogram.fsm.state import StatesGroup, State

from .dialog import Dialog
from .window import Window
from aiogram_dialog.widgets.kbd import Cancel, Keyboard, Start
from aiogram_dialog.widgets.text import Const, Jinja, Text


class AiogramDialogStates(StatesGroup):
    ABOUT = State()


async def metadata_getter(**_kwargs) -> dict:
    metadata = importlib.metadata.metadata("aiogram-dialog").json
    urls = [u.split(",", maxsplit=1) for u in metadata["project_url"]]
    return {
        "metadata": metadata,
        "urls":urls
    }


about_dialog = Dialog(
    Window(
        Jinja(
            "<b><u>{{metadata.name}}</u></b>\n"
            "\n"
            "{{metadata.summary}}\n"
            "\n"
            "<b>Version:</b> {{metadata.version}}\n"
            "<b>Author:</b> {{metadata.author_email}}\n"
            "\n"
            "{% for name, url in urls%}"
            "<b>{{name}}:</b> {{url}}\n"
            "{% endfor %}"
            "",
        ),
        Cancel(Const("Ok")),
        getter=metadata_getter,
        state=AiogramDialogStates.ABOUT,
        parse_mode="html",
        disable_web_page_preview=True,
    ),
)

DEFAULT_ABOUT_BTN_TEXT = Const("About aiogram-dialog")


def about_aiogram_dialog_button(text: Text = DEFAULT_ABOUT_BTN_TEXT) -> Keyboard:
    return Start(
        text=text, state=AiogramDialogStates.ABOUT,
        id="__aiogd_about__",
    )
