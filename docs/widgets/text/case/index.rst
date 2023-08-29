.. _case_text:

Case
*************

To select one of the texts depending on some condition you can use ``Case``.

To use this widget you have to specify at least two parameters:

* ``texts`` - dictionary, which contains options
* ``selector`` - expression wich is used to get the ``condition`` value that will be used to select which option of ``Case`` widget to show.

``selector`` can be:

* string key - this string will be used as a key of ``data`` dictionary to get the value of ``condition``
* magic-filter (``F``) - the result of resolving mafic-filter will be used as a ``condition``
* function - the result of this function will be used as a ``condition```

.. note::

   ``selector`` uses dynamic data. You need to either save this data in ``dialog_data`` beforehand or use ``getter`` to pass data to the widget (see :ref:`passing data<passing_data>`).


You can use ``...`` (Ellipsis object) as a key in ``texts`` dictionary to provide default option which will be used if no suitable options found.

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/case.png


.. autoclass:: aiogram_dialog.widgets.text.Case
   :special-members: __init__,
