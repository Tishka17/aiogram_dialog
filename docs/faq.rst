*********************************
Frequently asked questions (FAQ)
*********************************

How can I retrieve data from stateful widget (``Checkbox``, ``Multiselect``, etc)?
====================================================================================

If you have a global variable with widget you can use it with dialog_manager::

    widget.get_checked(manager)

Other option is to use widget id to get adapter and then call its methods::

    widget = dialog_manager.dialog().find('some_widget_id')
    widget.get_checked()

What is ``current_context().widget_data`` for?
================================================

This dictionary contains data stored by widgets themselves. Data structure is a matter of widget implementation so it should not be accessed directly. If you need to retrieve widget state use its methods.

How can I set a default value for a ``Musltiselect`` or a ``Radio``
=====================================================================

The better way is to state insed ``on_start`` callback of dialog.

How can I show ``Select`` widget in multiple rows? What about pagination?
===========================================================================

Wrap it with some layout widget like ``Group``, ``Column`` or ``ScrollingGroup``.

How can I show many buttons loaded from my database and paginate them?
========================================================================

Create ``Select`` widget and wrap it with ``ScrollingGroup``. In this case items should be loaded in window getter.

How can I show photo by its ``file_id``?
===========================================

You need to create custom widget. Use ``StaticMedia`` as a sample.

How can I request user location or contact?
===============================================

You need to send somehow a message with reply keyboard. You can use ``MessageInput`` to handle response within a window.


How can I show a list with URL buttons in a way similar to ``Select`` widget?
==============================================================================

Create a ``ListGroup`` and put there a ``Url`` widget.

How can I make library not to send new message when user sends a message himself?
====================================================================================

It is working this way because otherwise a dialog can be outside of user screen and he will loose it. If you still want to disable this feature you can add a MessageInput and then set ``dialog_manager.show_mode=ShowMode.EDIT`` inside handler.

How can I access middleware data inside dialog handlers or widgets?
===========================================================================

* In getter you will get it as kwargs
* In handlers it is available via ``dialog_manager.data``
* During rendering (like in ``Format``) it is passed as a ``middleware_data``

How can I find the current user?
=====================================

Get it as a ``dialog_manager.event.from_user``.

**Caution**: in case of background updates (done via ``BgManager``) it can contain only ``id``. If it is not suitable for you case set ``load=True`` while creating bg manager.


How can I pass data between dialogs?
=======================================

Input - pass via ``dialog_manager.start(..., data="here")``, read using ``dialog_manager.start_data``.
Output - pass via ``dialog_manager.done(result="here")``, read as a parameter to ``on_process_result`` of parent dialog

More details: :ref:`start-dialog`, :ref:`close-dialog`.