.. _jinja:

Jinja HTML rendering
***********************

It is very easy to create safe HTML messages using Jinja2 templates.
Documentation for template language is available at `official jinja web page <https://jinja.palletsprojects.com>`_

To use it you need to create text using ``Jinja`` class instead of ``Format`` and set proper ``parse_mode``.
If you do not want to set default parse mode for whole bot you can set it per-window.

For example you can use environment substitution, cycles and filters:

.. literalinclude:: ./example.py

It will be rendered to this HTML:

.. literalinclude:: ./example.html

In the example above the data from ``getter`` is used, but you can also access the data from ``dialog_data`` (e.g. ``{{ dialog_data['user']['weight'] }}``)


If you want to add custom `filters <https://jinja.palletsprojects.com/en/2.11.x/api/#custom-filters>`_
or do some configuration of jinja Environment you can setup it using ``aiogram_dialog.widgets.text.setup_jinja`` function
