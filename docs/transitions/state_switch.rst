.. _state_switch:
State switch
=================

Simplest thing you can do to change UI layout is to switch dialog state. It does not affect task stack and just draws another window.
Dialog context is kept the same, so all your data is still available.

There are several ways to do it:

* ``dialog_manager.switch_to`` method. Pass another state and window will be switched
* ``dialog_manager.next`` method. It will switch to the next window in the same order they were passed during dialog creation. Cannot be called when the last window is active
* ``dialog_manager.back`` method. Switch to the opposite direction (to the previous one). Cannot be called when the first window is active

Let's create thee windows with buttons and these transitions:

.. image:: /resources/switchstate.png

The code may look like:

.. literalinclude:: ./switch.py

It is ok to use these methods in message handler or if you have additional logic. But for simple cases it looks too complex.
To simplify it we have special types of buttons. Each one can contain custom text if needed:

* ``SwitchTo`` - calls ``switch_to`` when clicked. State is provided via constructor attribute
* ``Next`` - calls ``next`` when clicked
* ``Back`` - calls ``back`` when clicked

An example from above may be rewritten using these buttons:


.. literalinclude:: ./buttons.py


.. note::

    You can wonder, why we do not set an id to Back/Next buttons. Though it is normally recommended, these buttons do usually the same action so they have default ``id``.

    If you have multiple buttons of the same type in a window with ``on_click`` callback, you should explicitly set different ids.
