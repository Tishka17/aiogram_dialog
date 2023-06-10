.. _case_text:

Case
*************

To select one of the texts depending on some condition you should use ``Case``.

The condition can be either a data key, magic-filter or a function. The result of selector is check against provided texts dictionary.

You can use ``...`` (Ellipsis object) as a key to provide default text which is used when no suitable options found.

Code example:

.. literalinclude:: ./example.py

.. autoclass:: aiogram_dialog.widgets.text.Case
   :special-members: __init__,
