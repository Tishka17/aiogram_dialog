***********************************
Migration from previous versions
***********************************

Migration 2.0b10 -> 2.0b18
===============================

* ``Registry`` class removed.
* Each `Dialog`` is now a ``Router``. You should do ``dp.include_router(dialog)`` to attach it.
* ``setup_dialogs`` is now a replacement of ``registry.setup_dp()``. Parameters are the same.
* ``render_preview`` and ``render_transitions`` methods now expect ``Dispatcher``, ``Router`` or ``Dialog`` instance instead of ``Registry``
* ``aiogram-dialog-preview`` now expects ``Dispatcher``, ``Router`` or ``Dialog`` instance instead of ``Registry``

Migration 2.0b10 -> 2.0b17
===============================

* ``Registry`` is now created without dispatcher. After that you need to setup dispatcher using ``setup_dp`` method
* ``Registry.register_start_handler`` now requires router (or dispatcher)

Migration 1.x -> 2.0b10
==========================

* Main objects like ``Dialog``, ``LaunchMode`` and ``DialogManager`` should be imported directly from ``aiogram_dialog`` package.
* ``Whenable`` is moved to ``widgets.common`` subpackage
* When finding widget by ``id`` you will get managed version of widget. This objects no more expect ``DialogManager`` or ``ChatEvent`` arguments in their methods
* For ``ListGroup`` items callbacks you will get ``SubManager`` which behavior slightly changed.
* ``SubManager`` moved to ``aiogram_dialog`` package
* ``ManagedDialog`` protocol renamed to ``DialogProtocol``
* ``Dialog`` no more contains ``.next``, ``.back`` and ``.switch_to`` methods. They are available in ``DialogManager``
* ``DialogManagerFactory`` protocol simplified
* no more ``ManagedDialogAdapterProto``. You will get ``Dialog`` instance instead
* no more ``data`` in ``Context``. Renamed to ``start_data`` many time ago
* ``dialog_data`` and ``start_data`` added to ``DialogManager``, ``data`` is renamed to ``middleware_data``

Migration 0.11 -> 1.0
========================

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
