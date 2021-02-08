from aiogram_dialog import DialogRegistry

registry = DialogRegistry(dp)  # this is required to use `aiogram_dialog`
registry.register(dialog)  # register a dialog
