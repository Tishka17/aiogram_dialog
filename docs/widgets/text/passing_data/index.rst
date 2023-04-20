.. _passing_data:
Passing data
==================

Some widgets contain fixed text, others can show dynamic contents
For example:

* ``Const("Hello, {name}!")`` will be rendered as ``Hello, {name}!``
* ``Format("Hello, {name}!")`` will interpolate with window data and transformed to something like ``Hello, Tishka17!``

So, widgets can use data. But data must be loaded from somewhere. To do it Windows and Dialogs have ``getter`` attribute.
Getter can be either a function returning data or static dict or list of such objects.

So let's create a function and use it to enrich our window with data.

.. note::

    In this and later examples we will skip common bot creation and dialog registration code unless it has notable differences with quickstart

.. literalinclude:: ./example.py

It will look like:

.. image:: /resources/getter.png

Since version 1.6 you do not need getter to access some common objects:

* ``dialog_data`` -contents of corresponding field from current context. Normally it is used to store data between multiple calls and windows withing single dialog
* ``start_data`` - data passed during current dialog start. It is also accessible using ``current_context``
* ``middleware_data`` - data passed from middlewares to handler. Same as ``dialog_manager.data``
* ``event`` - current processing event which triggered window update. Be careful using it, because different types of events can cause refreshing same window.
