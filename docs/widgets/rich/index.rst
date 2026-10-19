.. _rich:

Rich
*************

Rich widgets are used to send window as a `rich message <https://core.telegram.org/bots/api#rich-messages>`_.
Rich messages support headings, lists, tables, media blocks, collapsible blocks, formulas and other structured formatting.

Rich widget is passed to ``Window`` as ``rich=`` argument. There are 3 variants of them:

* ``RichHtml``: window text is used as rich message content with `rich HTML style <https://core.telegram.org/bots/api#rich-message-formatting-options>`_.
* ``RichMarkdown``: window text is used as rich message content with `rich Markdown style <https://core.telegram.org/bots/api#rich-message-formatting-options>`_.
* ``RichBlocks``: window text is sent as a paragraph block. It is not parsed, so no formatting is applied to it.

``parse_mode`` of the window is ignored in all cases.

Inline keyboard of the window becomes a part of the rich message: each row is shown as a row of buttons after the text.
So any existing keyboard widget can be used, except buttons with ``pay`` or ``callback_game``.

Parameters:

* ``is_rtl``: if ``True``, the message is shown right-to-left.
* ``skip_entity_detection``: if ``True``, URLs, mentions, hashtags and other entities are not detected automatically.
* ``when``: condition to send window as a rich message. Otherwise, it is sent as a regular one.

Code example:

.. literalinclude:: ./example.py

.. note::

    Rich message cannot have a media attachment. If window has media, it is sent as a regular message with caption.
    Use media blocks inside the text instead: ``<img src="..."/>`` or ``![](...)``.

.. note::

    Buttons inside rich message cannot be removed without changing the message itself.
    So unlike regular inline keyboard, they stay in previous messages when new one is sent or dialog is closed.

.. tip::

    ``Format`` does not escape data. Use ``Jinja`` which escapes HTML by default, if you show user data in HTML.

.. autoclass:: aiogram_dialog.widgets.rich.RichHtml
   :special-members: __init__

.. autoclass:: aiogram_dialog.widgets.rich.RichMarkdown

.. autoclass:: aiogram_dialog.widgets.rich.RichBlocks
