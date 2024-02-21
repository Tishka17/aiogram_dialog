How are messages updated
=====================

ShowMode
********************

Currently, to manage the update of the dialog, we use the feature called ShowMode.

When we need to change show mode we can just use show_mode setter on DialogManager or pass it in DialogManager methods (.start, .update, .switch_to, etc.)

.. literalinclude:: ./example.py

.. important::

    ShowMode changes only for the next update and then returns to AUTO mode.

.. autoclass:: aiogram_dialog.api.entities.modes.ShowMode(Enum)
