.. _task_stack:
Task stack
===============

To deal with multiple opened dialogs **aiogram_dialog** has such thing as dialog stack. It allows dialogs to be opened one over another ("stacked") so only one of them is visible.

* Each time you start a dialog new task is added on top of a stack and new dialog context is created.
* Each time you close a dialog, task and dialog context are removed.

You can start same dialog multiple times, and multiple contexts (identified by ``intent_id``) will be added to stack preserving the order.
So you must be careful restarting you dialogs: do not forget to clear stack or it will eat all your memory

Starting with version 1.0 you can create new stacks but default one exists always.