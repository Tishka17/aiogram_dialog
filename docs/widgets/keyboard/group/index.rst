.. _group:

Group
*************

**Group** widget does more complex unions. By default, it places one keyboard below another. For example, you can stack multiple rows (or groups, or whatever)

.. literalinclude:: ./example.py

.. image:: /resources/group.png

Also it can be used to produce rows of fixed width. To do it just set ``width`` to desired value. ``Row`` and ``Column`` widgets are groups with predefined width.

.. literalinclude:: ./example_width.py

.. image:: /resources/group_width.png

Instead of a fixed number of buttons per row, you can wrap rows by the total
number of characters with ``width_symbols``. Buttons are packed greedily until
the summed length of their texts would exceed the limit; a button whose text is
longer than the limit still gets its own row. ``width`` and ``width_symbols``
are mutually exclusive - setting both raises ``ValueError``.

.. literalinclude:: ./example_width_symbols.py

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.group.Group
