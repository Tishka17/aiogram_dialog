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


So the main required thing is items. Normally it is a string with key in your window data. The value by this key must be a collection of any objects.
If you have a static list of items you can pass it directly to a select widget instead of providing data key.

Next important thing is ids. Besides a widget id you need a function which can return id (string or integer type) for any item.


.. literalinclude:: examples/widgets/select.py

.. image::  resources/select.png


.. note::

    Select places everything in single row. If it is not suitable for your case - simply wrap it with `Group`_ or `Column`_

