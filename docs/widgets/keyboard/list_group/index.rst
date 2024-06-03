.. _list_group:

ListGroup
*************

**ListGroup** is more complex way to render widgets for list of items. While ``Select`` generates simple buttons, with ``ListGroup`` you can create any set of keyboard widgets and repeat them.

To identity ``item`` inside keyboard event you can check ``dialog_manager.item_id``. This is possible because ``SubManager`` is passed instead of ``DialogManager`` while corresponding widget is located inside ``ListGroup``.

To find widget for specific ``item_id`` in a ``ListGroup``, you can use the ``.find_for_item`` method from ``ManagedListGroup``.


Manager methods:

* **.find**: if manager already adapted for current ``ListGroup`` row, finds the widget within the current manager (``SubManager``).

* **.find_in_parent**: if you need to find widgets outside the row, finds the widget within the parent manager (``DialogManager``).

.. note::

    If you nest a ``ListGroup`` in ``ListGroup`` your parent manager will be ``SubManager``

Code example:

.. literalinclude:: ./example.py
   :language: python

.. autoclass:: aiogram_dialog.widgets.kbd.ListGroup
   :special-members: __init__,

.. autoclass:: aiogram_dialog.widgets.kbd.ManagedListGroup
   :members: find_for_item

.. autoclass:: aiogram_dialog.manager.sub_manager.SubManager
