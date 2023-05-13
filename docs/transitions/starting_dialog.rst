.. _start-dialog:

Starting a dialog
=======================


Each dialog is like a function in python. Is has some input (``start_data``), output (``result``) and is local data (``dialog_data`` and ``widget_data``).
When you start dialog in same stack (not passing ``StartMode.NEW_STACK``) it is show "above" current dialog. User stop interacting with current dialog windows and sees new one from this moment.

Dialog is identified by his starting state and you need to pass it when starting a dialog. It doesn't have to be a first state in dialog, but be careful with it.
There are several ways to do it:

* call ``dialog_manager.start`` method.
* use ``Start`` keyboard widget, which calls same method by itself.

Started dialog will have his own empty context and has no access to parent one. You can specify its behavior passing some data to ``start`` method. It will be stored inside context and is available as ``dialog_manager.start_data``.

You can store data in ``dialog_manager.dialog_data`` and it will be kept until it is closed and accessed only within this dialog handlers. Stateful widgets store their data is similar way and it is also not shared across opened dialogs.

You have no limitations which dialog to start. You are limited only by a depth of a stack: no more than 100 dialogs can be placed in one stack simultaneously.
You can even open the same dialog multiple times and each time it will placed above and have new context.


.. literalinclude:: ./start.py