.. _request_poll:

RequestPoll
***********

**RequestPoll** is a single reply keyboard button that asks the user to create a poll and send it to the bot.

The button requires a text label. Optional parameter includes ``poll_type`` to specify type of the poll.

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/request_poll.png

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.request.RequestPoll
   :special-members: __init__