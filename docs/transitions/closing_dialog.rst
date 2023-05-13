.. _close-dialog:

Closing a dialog
=================


When dialog is closed it is removed from stack deleting context. From this moment user returns to a dialog which was underneath the current one.

To close a dialog you have to methods:

* call ``dialog_manager.done``.
* use ``Cancel`` button.

Parent dialog has no access to the context of child one. But you can pass some data as a result to ``done()`` method and then process it in ``on_process_result`` callback of parent dialog.


.. literalinclude:: ./done.py
