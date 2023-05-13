.. _static_media:

StaticMedia
*************

``StaticMedia`` allows you to share media files by their path os URLs. Though address supports string interpolation as it can be ``Text`` widget, other parameters remain static.

You can use it providing ``path`` or ``url`` to the file, it's ContentType and additional parameters if required.
Also you might need to change media type (``type=ContentType.Photo``) or provide any additional params supported by aiogram using ``media_params``

Be careful using relative paths. Mind the working directory.

.. literalinclude:: ./example.py

It will look like:

.. image::  /resources/static_media.png

For more complex cases you can read source code of ``StaticMedia`` and create your own widget with any logic you need.

.. note::

    Telegram allows to send files using ``file_id`` instead of uploading same file again.
    This make media sending much faster. ``aiogram_dialog`` uses this feature and caches sent file ids in memory

    If you want to persistent ``file_id`` cache, implement ``MediaIdStorageProtocol`` and pass instance to your dialog registry
