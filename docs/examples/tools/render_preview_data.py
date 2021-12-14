class RenderSG(StatesGroup):
    first = State()


dialog = Dialog(
    Window(
        Format("Hello, {name}"),
        Cancel(),
        state=RenderSG.first,
        preview_data={"name": "Tishka17"},
    ),
)
