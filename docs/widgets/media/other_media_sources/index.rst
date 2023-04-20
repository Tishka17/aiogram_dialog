;.. _other_media_sources:
Other media sources
*************

Sometimes you have some custom sources for media files: neither file in filesystem, not URL in the interner, nor existing file in telegram.
It could be some internal storage like database or private s3-compatible one or even runtime generated objects.

In this case recommended steps to solve a problem are:

1. Generate some custom URI identifying you media. It could be string like "bot://1234" or whatever you want
2. Inherit from ``MessageManager`` class and redefine ``get_media_source`` method to load data identified by your URI from custom source
3. Pass you message manager instance when constructing ``Registry``

With such implementation you will be able to implement custom media retrieving and keep usage of existing media widgets and file id caching
