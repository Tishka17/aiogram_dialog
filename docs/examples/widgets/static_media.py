from aiogram_dialog.widgets.media import StaticMedia

windows = Window(
    StaticMedia(
        path="/home/tishka17/python_logo.png"),
        type=ContentType.PHOTO,
    ),
    state=DialogSG.greeting,
)