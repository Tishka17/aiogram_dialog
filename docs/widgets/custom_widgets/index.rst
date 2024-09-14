.. _custom_widgets:

Custom widgets
*****************************

You can create custom widgets if your are not satisfied with existing ones.


If you are making Keyboard widget it is important to create ``InlineKeyboardButton`` instances on each rendering instead of reusing same instance. This is because dialogs modify ``callback_data`` in it.


* :ref:`SwitchInlineQueryCurrentChat<switch_inline_query_current_chat>` - opens inline query in current chat

.. toctree::
    :hidden:

    switch_inline_query_current_chat/index