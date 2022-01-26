class DialogsError(RuntimeError):
    pass


# intents and stack
class InvalidStackIdError(DialogsError):
    pass


class UnknownIntent(DialogsError):
    pass


class OutdatedIntent(DialogsError):
    def __init__(self, stack_id, text):
        super().__init__(text)
        self.stack_id = stack_id


class UnknownState(DialogsError):
    pass


class DialogStackOverflow(DialogsError):
    pass


# manager
class IncorrectBackgroundError(DialogsError):
    pass


# widgets
class InvalidWidgetIdError(DialogsError):
    pass


class InvalidWidget(DialogsError):
    pass


class InvalidWidgetType(InvalidWidget):
    pass
