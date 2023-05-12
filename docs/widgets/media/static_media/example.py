from aiogram.types import ContentType

from aiogram_dialog import Window
from aiogram_dialog.widgets.media import StaticMedia

windows = Window(
    StaticMedia(
        path="/home/tishka17/python_logo.png",
        type=ContentType.PHOTO,
    ),
)
