.. _toggle:

Toggle
*************

**Toggle** is a button that switches between elements when clicked. Works like a :ref:`Radio<radio>`.

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/toggle.gif

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.select.OnItemStateChanged
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.kbd.select.OnItemClick
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.kbd.select.Toggle
   :special-members: __init__,

.. autoclass:: aiogram_dialog.widgets.kbd.ManagedToggle
   :members: is_checked, get_checked, set_checked