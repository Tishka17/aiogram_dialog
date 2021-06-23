***********************************
Migration from previous versions
***********************************

Incompatible changes with 0.11:

* ``reset_stack`` was replaced with ``StartMode``. E.g. ``reset_stack=true`` is now ``mode=StartMode.RESET_STACK``
* dialog no more changes current aiogram state
* In manager ``context`` and ``current_intent()`` were replaced with ``current_context()`` call.
    * ``dialog_data`` is a dict to hold user data
    * ``widget_data`` is a dict to hold data of widgets
    * ``start_data`` is a data provided whe dialog start
    * ``state`` is current dialog state
* When subdialog finishes parent is restored with previous state, not which it was started
* Changed signature of ``on_process_result`` callback. It now accepts start data used to start subdialog
* ``Group.keep_rows`` option removed. Set ``width=None`` (default value) if you want to keep rows.
