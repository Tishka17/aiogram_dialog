from .context import Context


class IntentCompat:
    def __init__(self, context: Context):
        self.context = context

    @property
    def id(self):
        return self.context.id

    @property
    def name(self):
        return self.context.state.state

    def data(self):
        return self.context.start_data
