.. _link_preview:

LinkPreview
*************

The **LinkPreview** widget is used to manage link previews in messages.

Parameters:

* ``url``: A ``TextWidget`` with URL to be used in the link preview. If not provided, the first URL found in the message will be used.
* ``is_disabled``: that controls whether the link preview is displayed. If ``True``, the preview will be disabled.
* ``prefer_small_media``: that controls if the media in the link preview should be displayed in a smaller size. Ignored if media size change is not supported.
* ``prefer_large_media``: that controls if the media in the link preview should be enlarged. Ignored if media size change is not supported.
* ``show_above_text``: that specifies whether the link preview should be displayed above the message text. If ``True``, link preview be displayed above the message text.


Code example:

.. literalinclude:: ./example.py

.. autoclass:: aiogram_dialog.widgets.link_preview.LinkPreview
   :special-members: __init__
   :members: render_link_preview, _render_link_preview
