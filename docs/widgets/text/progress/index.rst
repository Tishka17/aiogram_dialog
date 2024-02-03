.. _progress_bar:

Progress
*************

The `Progress` widget is used when you need to display the progress of a process.

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/progress.png

.. admonition:: Prevent new messages while Progress is running
    :class: hint

    When Progress is running and the user sends a message to the bot, aiogram_dialog automatically updates the window and sends a new message.
    However, you can prevent this by using :ref:`MessageInput <message_input>` and a handler that sets ShowMode to EDIT mode.

.. literalinclude:: ./prevent_new_message.py

.. admonition:: Allow the bot to be used while Progress running
    :class: hint

    If you want to allow the user to use the bot while Progress is running, you can open a window through a background manager, pass a stack_id, and use that manager in a background task.

.. literalinclude:: ./bg_manager_example.py