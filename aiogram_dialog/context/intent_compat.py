from .intent import Intent


class IntentCompat:
    def __init__(self, intent: Intent):
        self.intent = intent

    @property
    def id(self):
        return self.intent.id

    @property
    def name(self):
        return self.intent.state.state

    def data(self):
        return self.intent.start_data
