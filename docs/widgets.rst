**********************
Widgets and rendering
**********************

Passing data
==================

Some widgets contain fixed text, others can show dynamic contents
For example:

* ``Const("Hello, {name}!")`` will be rendered as ``Hello, {name}!``
* ``Format("Hello, {name}!")`` will interpolate with window data and transformed to something like ``Hello, Tishka17!``

So, widgets can use data. But data must be loaded from somewhere. To do it Windows has `getter` attribute.
So let's create a function and use it to enrich our window with data.

.. note::

    In this and later examples we will skip common bot creation and dialog registration code unless it has notable differences with quickstart

.. literalinclude:: examples/widgets/getter.py

It will look like:

.. image:: resources/getter.png


Widget types
==================

Base information
********************

Currently there are 2 kinds of widgets: `texts <Text widget types_>`_ and `keyboards <Keyboard widget types_>`_.

* **Texts** used to render text anywhere in dialog. It can be message text, button title and so on.
* **Keyboards** represent parts of ``InlineKeyboard``

Also there are 2 general types:

* ``Whenable`` is used to hide widget depending on data or some conditions. Currently al widgets are whenable.
  See: `Hiding widgets`_
* ``Actionable`` is any widget with action (currently only any type of keyboard). It has ``id`` and can be found by that id.
  It recommended for all stateful widgets (e.g Checkboxes) to have unique id within dialog.
  Buttons with different behavior also must have different ids.


Text widget types
*****************************

Every time you need to render text use any of text widgets:

* ``Const`` - returns text with no midifications
* ``Format`` - formats text using ``format`` function. If used in window the data is retrived via ``getter`` funcion.
* ``Multi`` - multiple texts, joined with a separator (``sep=``)
* ``Case`` - shows one of texts based on condition
* ``Progress`` - shows a progress bar
* ``Jinja`` - represents a HTML rendered using jinja2 template

Keyboard widget types
*****************************

Each keyboard provides one or multiple inline buttons. Text on button is rendered using text widget

* ``Button`` - single inline button. User provided ``on_click`` method is called when it is clicked.
* ``Group`` - any group of keyboards. By default, they are rendered one above other. Also you can rearrange buttons in new rows of provided width
* ``Row`` - simplified version of group. All buttons placed in single row.
* ``Column`` - another simplified version of group. All buttons placed in single column (one per row).
* ``Uri`` - single inline button with uri
* ``SwitchState`` - switches window within a dialog using provided state
* ``Next``/``Back`` - switches state forward or backward
* ``Start`` - starts a new dialog with no params
* ``Cancel`` - closes the current dialog with no result. An underlying dialog is shown
* ``Select`` - select one or multiple items. Items can be provided in constructor or passed from data getter of a window

Combining texts
=================

To combine multiple texts you can use ``Multi`` widget. You can use any texts inside it. Also you can provide a string separator

.. literalinclude:: examples/widgets/multi.py

To select one of the texts depending on some condition you should use ``Case``.
The condition can be either a data key or a function:

.. literalinclude:: examples/widgets/case.py

Keyboards
================


Hiding widgets
====================

