.. _text_input:

TextInput
*************

The **TextInput** widget automatically saving and validating text for later processing in the dialog.

Parameters:

* ``type_factory``: allows for input validation and automatic conversion to the specified type.
* ``on_success``: for handling successful input.
* ``on_error``:  for error handling, will work if ``type_factory`` throws ValueError.
* ``filter``: support `aiogram <https://docs.aiogram.dev/en/latest/dispatcher/filters/index.html>`_ filters.

Code example:

.. literalinclude:: ./example.py

.. autoclass:: aiogram_dialog.widgets.input.text.OnSuccess
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.input.text.OnError
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.input.text.TextInput
   :special-members: __init__

.. autoclass:: aiogram_dialog.widgets.input.text.ManagedTextInput
   :members: get_value