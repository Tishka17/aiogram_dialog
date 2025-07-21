.. _switch_inline_query_chosen_chat:

SwitchInlineQueryChosenChatButton
*********************************

**SwitchInlineQueryChosenChatButton** is a single inline button that prompts the user to select one of their chats based on the specified scopes, opens the selected chat, and inserts the bot's username and the given inline query into the input field.

The button requires a text label and query text. You can specify which chat types the user can select by using the following parameters: ``allow_user_chats``, ``allow_bot_chats``, ``allow_group_chats``, ``allow_channel_chats``.

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/switch_inline_query_chosen_chat.png

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.button.SwitchInlineQueryChosenChatButton
   :special-members: __init__