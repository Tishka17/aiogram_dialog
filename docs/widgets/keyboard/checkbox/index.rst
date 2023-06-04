.. _checkbox:

Checkbox
*************

Some of the widgets are stateful. They have some state which is affected by on user clicks.

One of such widgets is **Checkbox**. It can be in checked and unchecked state represented by two texts.
On each click it inverses its state.

If a dialog with checkbox is visible, you can check its state by calling ``is_checked`` method and change it calling ``set_checked``

As button has ``on_click`` callback, checkbox has ``on_state_changed`` which is called each time state switched regardless the reason

.. literalinclude:: ./example.py

.. image:: /resources/checkbox_checked.png
.. image:: /resources/checkbox_unchecked.png


.. note::

    State of widget is stored separately for each separate opened dialog. But all windows in dialog share same storage. So, multiple widgets with same id will share state.
    But at the same time if you open several copies of same dialogs they will not mix their states
