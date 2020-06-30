from .dialog import Dialog


class DialogResumer:
    def __init__(self, *dialogs: Dialog):
        self.dialogs = dialogs

    async def __call__(self, *args, **kwargs):
        for d in self.dialogs:
            if d.resume(*args, **kwargs):
                return True
        return False
