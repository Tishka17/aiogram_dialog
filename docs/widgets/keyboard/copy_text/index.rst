.. _copy_text:

CopyText
--------

``CopyText`` represents a button that copies specified text to the user's clipboard when clicked. It uses Telegram's native ``CopyTextButton``.
It requires two text arguments (which can be any text widgets like ``Const`` or ``Format``):

* ``text``: The label displayed on the button.
* ``copy_text``: The actual text that will be copied to the clipboard.

.. literalinclude:: ./example.py

.. image:: /resources/copy_text.png

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.copy.CopyText
