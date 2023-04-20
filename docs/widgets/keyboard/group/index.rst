.. _group:
Group
*************

**Group** widget does more complex unions. By default, it places one keyboard below another. For example, you can stack multiple rows (or groups, or whatever)

.. literalinclude:: ./example.py

.. image:: /resources/group.png

Also it can be used to produce rows of fixed width. To do it just set ``width`` to desired value. ``Row`` and ``Column`` widgets are groups with predefined width.

.. literalinclude:: ./example_width.py

.. image:: /resources/group_width.png