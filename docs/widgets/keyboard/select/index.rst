.. _select:

Select
*************

**Select** acts like a group of buttons but data is provided dynamically.
It is mainly intended to use for selection a item from a list.

Normally text of selection buttons is dynamic (e.g. ``Format``).
During rendering an item text, it is passed a dictionary with:

* ``item`` - current item itself
* ``data`` - original window data
* ``pos`` - position of item in current items list starting from 1
* ``pos0`` - position starting from 0


So the main required thing is ``items``. You have 4 options to specify this parameter:

* String with key in your window data (e.g. ``items="fruits"```). The value by this key must be a collection of any objects.
* Static list of items (e.g. ``items=['apple', 'banana', 'orange']``).
* Magic filter (e.g. ``items=F["fruits"]``). Filter has to return collection of elements.
* Function with one parameter (``data: Dict``) that returns collection of elements (e.g. ``items=lambda d: d["fruits"]``)


Next important thing is ids. Besides a widget id you need a function which can return id (string or integer type) for any item.


.. literalinclude:: ./example.py

.. image::  /resources/select.png


.. note::

    Select places everything in single row. If it is not suitable for your case - simply wrap it with :ref:`group` or :ref:`column`



Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.select.OnItemClick
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.kbd.Select
   :special-members: __init__