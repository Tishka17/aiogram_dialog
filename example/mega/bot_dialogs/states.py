from aiogram.fsm.state import State, StatesGroup


class Scrolls(StatesGroup):
    MAIN = State()
    DEFAULT_PAGER = State()
    PAGERS = State()
    LIST = State()
    TEXT = State()
    STUB = State()
    SYNC = State()


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
    TOGGLE = State()


class Calendar(StatesGroup):
    MAIN = State()
    DEFAULT = State()
    CUSTOM = State()


class Counter(StatesGroup):
    MAIN = State()


class Multiwidget(StatesGroup):
    MAIN = State()

class ReplyKeyboard(StatesGroup):
    MAIN = State()


class Switch(StatesGroup):
    MAIN = State()
    INPUT = State()
    LAST = State()
