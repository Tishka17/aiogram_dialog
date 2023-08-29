from aiogram.enums import ContentType
from aiogram.fsm.state import StatesGroup, State

from aiogram_dialog import Dialog, Window
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.media import DynamicMedia


class Main(StatesGroup):
    menu = State()


async def get_data(**kwargs):
    image_id = "AgACAgIAAxkBAAICaGRBazvG-8X5riVWiz3vF9aW5LPqAAI8xjEbzg4ISoMkVbG_PhpbAQADAgADdwADLwQ"  # Your file_id
    image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(image_id))
    return {'photo': image}


dialog = Dialog(
    Window(
        DynamicMedia("photo"),
        state=Main.menu,
        getter=get_data,
    ),
)
