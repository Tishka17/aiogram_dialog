.. _counter:

Counter
*************

Counter widget is a simple way to input a number using ``+``/``-`` buttons.


.. literalinclude:: ./example.py

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.counter.OnCounterEvent
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.kbd.Counter
   :special-members: __init__,

.. autoclass:: aiogram_dialog.widgets.kbd.ManagedCounterAdapter
   :members: get_value, set_value
