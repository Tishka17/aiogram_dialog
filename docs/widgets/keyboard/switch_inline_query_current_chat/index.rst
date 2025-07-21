.. _switch_inline_query_current_chat:

SwitchInlineQueryCurrentChat
*****************************

**SwitchInlineQueryCurrentChat** is a single inline button that inserts the bot's username and specified inline query into the current chat's input field.

The button requires a text label and query text.

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/switch_inline_query_current_chat.png

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.button.SwitchInlineQueryCurrentChat
   :special-members: __init__