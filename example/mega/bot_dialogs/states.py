from aiogram.fsm.state import State, StatesGroup


class Scrolls(StatesGroup):
    MAIN = State()
    DEFAULT_PAGER = State()
    PAGERS = State()
    TEXT = State()
    STUB = State()


class Main(StatesGroup):
    MAIN = State()

class Calendar(StatesGroup):
    MAIN = State()