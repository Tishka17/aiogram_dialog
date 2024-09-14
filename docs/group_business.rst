******************************************
Groups and business chats
******************************************

.. warning::
    Telegram has very strong limitations on amount of operations in groups,
    so it is not recommended to use interactive menus there

Support of groups, supergroups and business chats is based on usage of additional dialog stacks.

Starting shared dialogs
=================================

When user sends message or other event not attached directly to some dialog, default stack is used. If you start dialogs in that stack, they can be accessed only by that user. So, the default stack in **personal**.

To send a *shared* dialog from *personal*, you need to use other stacks. It can be ``aiogram_dialog.GROUP_STACK_ID``, other predefined string or starting via ``StartMode.NEW_STACK``.

.. code-block:: python

    bg = dialog_manager.bg(stack_id=GROUP_STACK_ID)
    bg.start(
        MyStateGroup.MY_STATE,
        mode=StartMode.RESET_STACK,
    )

If there are different topics in chat, stacks between them are isolated. To start dialog in different topic pass ``thread_id`` as ``.bg()`` argument

Limiting access
======================

To set limitations on who can interact with that dialog, you can pass ``AccessSettings`` when starting new dialog. If not access settings are set, they will be copied from last opened dialog in stack.

.. code-block:: python

    dialog_manager.start(
        MyStateGroup.MY_STATE,
        mode=StartMode.RESET_STACK,
        access_settings=AccessSettings(user_ids=[123456]),
    )

In this example, pre-defined group stack will be used and new dialogs will be available only for user with id ``123456``. If later user clicks on a specific dialog, stack of that dialog is used, so you won't need to call ``.bg()``

Currently, only check by ``user.id`` is supported, but you bring your own logic implementing ``StackAccessValidator`` protocol and passing it so ``setup_dialogs`` function.

Handling forbidden interactions
=================================

If user is not allowed to interact with dialog his event is not routed to dialogs and you can handle it in aiogram. To filter this situation you can rely on ``aiogd_stack_forbidden`` key of middleware data.

Classes
===========


.. autoclass:: aiogram_dialog.AccessSettings


.. autoclass:: aiogram_dialog.api.protocols.StackAccessValidator
   :members: is_allowed
