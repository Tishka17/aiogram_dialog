Widgets and Rendering
=====================

Base information
********************

Currently there are 4 kinds of widgets: :ref:`texts <text_widgets>`, :ref:`keyboards <keyboard_widgets>`,
:ref:`input <input_widgets>`, :ref:`media<media_widgets>` and you can create your own :ref:`widgets<custom_widgets>`.

* **Texts** used to render text anywhere in dialog. It can be message text, button title and so on.
* **Keyboards** represent parts of ``InlineKeyboard``
* **Media** represent media attachment to message
* **Input** allows to process incoming messages from user. Is has no representation.

Also there are 2 general types:

* ``Whenable`` can be hidden or shown depending on data or some conditions. Currently all widgets are whenable.
  See: :ref:`Hiding widgets<hiding_widgets>`
* ``Actionable`` is any widget with action (currently only any type of keyboard). It has ``id`` and can be found by that id.
  It recommended for all stateful widgets (e.g Checkboxes) to have unique id within dialog.
  Buttons with different behavior also must have different ids.

.. note::

  Widget id can contain only ascii letters, numbers, underscore and dot symbol.

  * ``123``, ``com.mysite.id``, ``my_item`` - valid ids
  * ``hello world``, ``my:item``, ``птичка`` - invalid ids

.. toctree::
    text/index
    keyboard/index
    input/index
    media/index
    hiding/index
    custom_widgets/index


