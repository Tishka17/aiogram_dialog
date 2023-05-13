.. _radio:

Radio
*************

**Radio** is stateful version of select widget. It marks each clicked item as checked deselecting others.
It stores which item is selected so it can be accessed later

Unlike for the ``Select`` you need two texts. First one is used to render checked item, second one is for unchecked.  Passed data is the same as for ``Select``

Unlike in normal buttons and window they are used to render an item, but not the window data itself.

Also you can provide ``on_state_changed`` callback function. It will be called when selected item is changed.

.. literalinclude:: ./example.py

.. image::  /resources/radio.png

Useful methods:

* ``get_checked`` - returns an id of selected items
* ``is_checked`` - returns if certain id is currently selected
* ``set_checked`` - sets the selected item by id
