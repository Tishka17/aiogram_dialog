.. _multiselect:
Multiselect
*************

**Multiselect** is another kind of stateful selection widget.
It very similar to ``Radio`` but remembers multiple selected items

Same as for ``Radio`` you should pass two texts (for checked and unchecked items). Passed data is the same as for ``Select``


.. literalinclude:: ./example.py

After few clicks it will look like:

.. image::  /resources/multiselect.png

Other useful options are:

* ``min_selected`` - limits minimal number of selected items ignoring clicks if this restriction is violated. It does not affect initial state.
* ``max_selected`` - limits maximal number of selected items
* ``on_state_changed`` - callback function. Called when item changes selected state

To work with selection you can use this methods:

* ``get_checked`` - returns a list of ids of all selected items
* ``is_checked`` - returns if certain id is currently selected
* ``set_checked`` - changes selection state of provided id
* ``reset_checked`` - resets all checked items to unchecked state

.. warning::

    ``Multiselect`` widgets stores state of all checked items even if they disappear from window data.
    It is very useful when you have pagination, but might be unexpected when data is really removed.
