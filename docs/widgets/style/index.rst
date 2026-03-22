.. _style:

Button style types
********************

Style widgets can be used to customize most of keyboard widgets (e.g ``Button``, ``Checkbox`` or ``Calendar``). This includes color style (primary/danger/success) and emoji.

.. code-block:: python

    from aiogram.enums import ButtonStyle
    from aiogram_dialog.widgets.style import Style
    from aiogram_dialog.widgets.kbd import Button
    from aiogram_dialog.widgets.text import Const


    button = Button(
        Const("Ok"),
        id="okbtn",
        style=Style(style=ButtonStyle.PRIMARY, emoji_id="xxx"),
    )

``Style`` widget can have ``when=`` condition. Also, style widgets can be combined using operator ``|`` which requests data style/emoji from the next widgets if the first one returned None.


.. autoclass:: aiogram_dialog.widgets.style.Style
   :special-members: __init__