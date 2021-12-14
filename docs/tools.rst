***********************************
Helper tools (experimental)
***********************************

State diagram
=================

You can generate image with your states and transitions.

Firstly you need to install [graphviz](https://graphviz.org/download/) into your system.
Check installation instructions on official site.

Install library with tools extras:

.. literalinclude:: examples/tools/install.sh

Import rendering method:

.. literalinclude:: examples/tools/import.py


Call it passing your registry or list of dialogs:

.. literalinclude:: examples/tools/render.py

Run your code and you will get ``aiogram_dialog.png`` in working directory:


.. image:: resources/render_simple.png


State transition hints
-------------------------

You may notice, that not all transitions are show on diagram.
This is because library cannot analyze source code of you callbacks.
Only transitions, done by special buttons are shown.

To fix this behavior you can set ``preview_add_transitions`` parameter of window:

.. literalinclude:: examples/tools/render_hints.py

Run the code and check updated rendering result:

.. image:: resources/render_hints.png


Dialogs preview
=================


Import rendering method:

.. literalinclude:: examples/tools/import_preview.py

Add some data to be shown on preview using ``preview_data`` parameter of window:

.. literalinclude:: examples/tools/render_preview_data.py

Call it passing your registry and filename somewhere inside your asyncio code:

.. literalinclude:: examples/tools/render_preview.py

Together it will be something like this:

.. literalinclude:: examples/tools/preview_summary.py

As a result you will see a html file in working directory, that can be opened in browser to preview how all dialogs will look like.

.. image:: resources/render_preview_result.png