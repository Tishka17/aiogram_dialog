.. _passing_data:

Passing data
==================

In your dialogs you can show static data (just text) and dynamic data (variable value).
You have access to the following dynamic data:

* ``event`` - currently processed event which triggered window update. Be careful using it, because different types of events can cause refreshing same window
* ``middleware_data`` - data passed from middlewares to handler
* ``start_data`` - data that was passed when the current dialog was started. These data is stored in the aiogram FSM storage.
* ``dialog_data`` - you can use this dict to store dialog-related data. It will be accessible at all windows of current dialog. These data is stored in the aiogram FSM storage.

In addition you can specify getter-functions for dialog and window.
Getter-function has to return a dictionary.

Library collects all the data above into one dictionary object and passes this object to widgets.

Let's look at the example:

.. note::

    In this and later examples we will skip common bot creation and dialog registration code unless it has notable differences with quickstart

.. literalinclude:: ./example.py

Result:

.. image:: /resources/passing_data_example.png

In event handlers you don't have access to that dictionary, but you can acess ``event``, ``middleware_data``, ``start_data``, ``dialog_data`` via dialog_manager:

.. literalinclude:: ./data_in_handlers.py


You can find more examples of accessing dynamic data from various widgets in documentation for these widgets.
