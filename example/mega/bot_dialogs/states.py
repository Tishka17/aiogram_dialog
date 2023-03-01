from aiogram.fsm.state import State, StatesGroup


class Scrolls(StatesGroup):
    MAIN = State()
    DEFAULT_PAGER = State()
    PAGERS = State()
    TEXT = State()
    STUB = State()


class Main(StatesGroup):
    MAIN = State()


class Layouts(StatesGroup):
    MAIN = State()
    ROW = State()
    COLUMN = State()
    GROUP = State()


class Selects(StatesGroup):
    MAIN = State()
    SELECT = State()
    RADIO = State()
    MULTI = State()


class Calendar(StatesGroup):
    MAIN = State()
