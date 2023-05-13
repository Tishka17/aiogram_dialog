.. _types:

Types of transitions
========================

Talking to user you will need to switch between different chat states. It can be done using four types of transitions:

* *State switch* inside dialog. Doing so you will just show another window.
* *Start* a dialog in same stack. In this case dialog will be added to task stack with empty dialog context and corresponding window will be shown instead on previously visible one
* *Start* a dialog in new stack. In this case dialog will be shown in a new message and behave independently from current one.
* *Close* dialog. Dialog will be removed from stack, its data erased. underlying dialog will be shown

.. image:: /resources/stack_transitions.png