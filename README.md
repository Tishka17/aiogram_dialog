
[![PyPI version](https://badge.fury.io/py/aiogram-dialog.svg)](https://badge.fury.io/py/aiogram-dialog)
[![downloads](https://img.shields.io/pypi/dm/aiogram_dialog.svg)](https://pypistats.org/packages/aiogram_dialog)
[![license](https://img.shields.io/github/license/Tishka17/aiogram_dialog.svg)](https://github.com/Tishka17/aiogram_dialog/blob/master/LICENSE)

### About

Aiogram-dialog is a GUI framework for telegram bot. It is inspired by ideas of Android SDK and React.js

### Quickstart

1. Install:

```bash
pip install aiogram_dialog
```

2. See [examples](example)

3. Read the [documetntation](https://aiogram_dialog.readthedocs.org)

### Usage

#### Declaring Window

Each window consists of:

* Text widget. Renders text of message.
* Keyboard widget. Render inline keyboard
* Message handler. Called when user sends a message when window is shown
* Data getter function (`getter=`). Loads data from any source which can be used in text/keyboard
* State. Used when switching between windows

**Info:** always create `State` inside `StatesGroup`

A minimal window is:

```python
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog.widgets.text import Const
from aiogram_dialog import Window


class MySG(StatesGroup):
    main = State()


Window(
    Const("Hello, unknown person"),
    state=MySG.main,
),
```

More realistic example:

```python
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import Window


class MySG(StatesGroup):
    main = State()


async def get_data(**kwargs):
    return {"name": "world"}


Window(
    Format("Hello, {name}!"),
    Button(Const("Empty button"), id="nothing"),
    state=MySG.main,
    getter=get_data,
),
```

More complex window with multiple texts, button groups and selects can look like:

![window example](docs/resources/window_example.png)

And if we draw red border around each widget it will be:

![window example](docs/resources/layout_example.png)

### Declaring dialog

Window itself can do nothing, just send message. To use it you need dialog:

```python
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram_dialog import Dialog, Window


class MySG(StatesGroup):
    first = State()
    second = State()


dialog = Dialog(
    Window(..., state=MySG.first),
    Window(..., state=MySG.second),
)
```

**Info:** All windows in a dialog MUST have states from then same `StatesGroup`

After creating dialog you need to register it using `DialogRegistry`:

```python
from aiogram import Dispatcher
from aiogram_dialog import DialogRegistry

...
dp = Dispatcher(bot, storage=storage)  # create as usual
registry = DialogRegistry(dp)  # create registry
registry.register(name_dialog)  # create
```

**Info:** aiogram_dialog uses aiograms's FSM, so you need to create Dispatcher with suitable storage. Also avoid using
FSMContext directly

Then start dialog when you are ready to use it. Dialog is started via `start` method of `DialogManager` instance. You
should provide corresponding state to switch into (usually it is state of first window in dialog).

For example in `/start` command handler:

```python
@dp.message_handler(commands=["start"])
async def user_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MySG.first, reset_stack=True)
```

**Info:** Always set `reset_stack=True` in your top level start command. Otherwise, dialogs are stacked just as they do
on your mobile phone, so you can reach stackoverflow error

### Widgets

For picture above we have such widgets:

![window example](docs/resources/layout_example2.png)

#### Text widget types

Every time you need to render text use any of text widgets:

* `Const` - returns text with no midifications
* `Format` - formats text using `format` function. If used in window the data is retrived via `getter` funcion.
* `Multi` - multiple texts, joined with a separator (`sep=`)
* `Case` - shows one of texts based on condition
* `Progress` - shows a progress bar
* `Jinja` - represents a HTML rendered using jinja2 template

#### Keyboard widget types

Each keyboard provides one or multiple inline buttons. Text on button is rendered using text widget

* `Button` - single inline button. User provided `on_click` method is called when it is clicked.
* `Group` - any group of keyboards. By default, they are rendered one above other. Also you can rearrange buttons in new rows of provided width
* `Row` - simplified version of group. All buttons placed in single row. 
* `Column` - another simplified version of group. All buttons placed in single column (one per row). 
* `Url` - single inline button with url
* `SwitchTo` - switches window within a dialog using provided state
* `Next`/`Back` - switches state forward or backward
* `Start` - starts a new dialog with no params
* `Cancel` - closes the current dialog with no result. An underlying dialog is shown
* `Select` - dynamic group of buttons
* `Radio` - switch between multiple items. Like select but stores chosen item and renders it differently.   
* `Multiselect` - selection of multiple items. Like select/radio but stores all chosen items and renders them differently.   
