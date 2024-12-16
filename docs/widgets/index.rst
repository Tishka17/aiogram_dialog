Widgets and Rendering
=====================

Base information
********************

Currently there are 5 kinds of widgets: :ref:`texts <text_widgets>`, :ref:`keyboards <keyboard_widgets>`,
:ref:`input <input_widgets>`, :ref:`media<media_widgets>`, :ref:`link preview<link_preview>` and you can create your own :ref:`widgets<custom_widgets>`.

* **Texts** used to render text anywhere in dialog. It can be message text, button title and so on.
* **Keyboards** represent parts of ``InlineKeyboard``
* **Media** represent media attachment to message
* **Input** allows to process incoming messages from user. Is has no representation.
* **Link Preview** used to manage link previews in messages.

Widgets can display static (e.g. ``Const``) and dynamic (e.g. ``Format``) content. To use dynamic data you have to set it. See :ref:`passing data <passing_data>`.

Also there are 2 general types:

* ``Whenable`` can be hidden or shown depending on data or some conditions. Currently all widgets are whenable.
  See: :ref:`Hiding widgets<hiding_widgets>`
* ``Actionable`` is any widget with action (currently only any type of keyboard). It has ``id`` and can be found by that id.
  It's recommended for all stateful widgets (e.g Checkboxes) to have unique id within dialog.
  Buttons with different behavior also must have different ids.

.. note::

  Widget id can contain only ascii letters, numbers, underscore and dot symbol.

  * ``123``, ``com.mysite.id``, ``my_item`` - valid ids
  * ``hello world``, ``my:item``, ``птичка`` - invalid ids

.. toctree::
    :maxdepth: 1

    passing_data/index
    text/index
    keyboard/index
    input/index
    media/index
    link_preview/index
    hiding/index
    custom_widgets/index