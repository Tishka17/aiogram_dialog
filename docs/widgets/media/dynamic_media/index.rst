.. _dynamic_media:
DynamicMedia
*************

``StaticMedia`` allows you to share any supported media files. Just return a ``MediaAttachment`` from data getter and set ``selector`` for a field name.
Other option is to pass a callable returning ``MediaAttachment`` as a selector