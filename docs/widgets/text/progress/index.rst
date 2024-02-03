.. _progress_bar:

Progress
*************

The `Progress` widget is used when you need to display the progress of a process.

.. hint::
    When Progress is running and the user sends a message to the bot, aiogram_dialog automatically updates the window and sends a new message.
    However, you can prevent this by using :ref:`MessageInput <message_input>` and a handler that sets ShowMode to EDIT mode.

    Code example:

    .. literalinclude:: ./prevent_new_message.py

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/progress.png
