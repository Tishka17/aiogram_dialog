.. _transitions:

Transitions
*****************************

Types of transitions
========================

Talking to user you will need to switch between different chat states. It can be done using four types of transitions:

* *State switch* inside dialog. Doing so you will just show another window.
* *Start* a dialog in same stack. In this case dialog will be added to task stack with empty dialog context and corresponding window will be shown instead on previously visible one
* *Start* a dialog in new stack. In this case dialog will be shown in a new message and behave independently from current one.
* *Close* dialog. Dialog will be removed from stack, its data erased. underlying dialog will be shown

.. image:: /resources/stack_transitions.png


Task stack
===============

To deal with multiple opened dialogs **aiogram_dialog** has such thing as dialog stack. It allows dialogs to be opened one over another ("stacked") so only one of them is visible.

* Each time you start a dialog new task is added on top of a stack and new dialog context is created.
* Each time you close a dialog, task and dialog context are removed.

You can start same dialog multiple times, and multiple contexts (identified by ``intent_id``) will be added to stack preserving the order.
So you must be careful restarting you dialogs: do not forget to clear stack or it will eat all your memory

Starting with version 1.0 you can create new stacks but default one exists always.


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

.. _start-dialog:

Starting a dialog
=======================

Each dialog is like a function in python. Is has some input (``start_data``), output (``result``) and is local data (``dialog_data`` and ``widget_data``).
When you start dialog in same stack (not passing ``StartMode.NEW_STACK``) it is show "above" current dialog. User stop interacting with current dialog windows and sees new one from this moment.

Dialog is identified by his starting state and you need to pass it when starting a dialog. It doesn't have to be a first state in dialog, but be careful with it.
There are several ways to do it:

* call ``dialog_manager.start`` method.
* use ``Start`` keyboard widget, which calls same method by itself.

Started dialog will have his own empty context and has no access to parent one. You can specify its behavior passing some data to ``start`` method. It will be stored inside context and is available as ``dialog_manager.start_data``.

You can store data in ``dialog_manager.dialog_data`` and it will be kept until it is closed and accessed only within this dialog handlers. Stateful widgets store their data is similar way and it is also not shared across opened dialogs.

You have no limitations which dialog to start. You are limited only by a depth of a stack: no more than 100 dialogs can be placed in one stack simultaneously.
You can even open the same dialog multiple times and each time it will placed above and have new context.

.. literalinclude:: ./start.py

.. _close-dialog:

Closing a dialog
=================

When dialog is closed it is removed from stack deleting context. From this moment user returns to a dialog which was underneath the current one.

To close a dialog you have to methods:

* call ``dialog_manager.done``.
* use ``Cancel`` button.

Parent dialog has no access to the context of child one. But you can pass some data as a result to ``done()`` method and then process it in ``on_process_result`` callback of parent dialog.

.. literalinclude:: ./done.py
