.. _switch_inline_query:

SwitchInlineQuery
*******************

SwitchInlineQuery is a special kind of inline keyboard button that will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified inline query in the input field. May be empty, in which case just the bot's username will be inserted.

You can additionally specify a text that will occur in the query field (e.g. @mytestbot some query)

.. literalinclude:: ./example.py
