.. _list_text:

List
*************

The List widget is used when you need to display a list of items, works like the :ref:`Select widget<select>`.

.. literalinclude:: ./example.py

Result:

.. image:: /resources/list.png


Additionally, you can provide ``page_size`` and ``id`` so the ``List`` will allow you to paginate its items.
You can combine it with ``Pager`` widgets to switch pages.