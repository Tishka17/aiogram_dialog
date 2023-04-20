.. _button:
Button
*************

In simple case you can use keyboard consisting of single button. Button consts of text, id, on-click callback and when condition.

Text can be any ``Text`` widget, that represents plain text. It will receive window data so your button will have dynamic caption

Callback is normal async function. It is called when user clicks a button
Unlike normal handlers you should not call callback.answer(), as it is done automatically.

.. literalinclude:: ./example.py

.. image:: /resources/button.png

If it is unclear to you where to put button, check :ref:`quickstart`