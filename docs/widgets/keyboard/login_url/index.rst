.. _login_url:

LoginURLButton
*************

**LoginURLButton** is a single inline button with HTTPS URL used to automatically authorize the user.

The button requires a text label and authentication URL. Optional parameters include ``forward_text``, ``bot_username``, and ``request_write_access``.

Code example:

.. literalinclude:: ./example.py

Result:

.. image:: /resources/login_url.png

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.button.LoginURLButton
   :special-members: __init__