.. _calendar:

Calendar
*************

Basic usage
================

**Calendar** widget allows you to display the keyboard in the form of a calendar, flip through the months and select the date.
The initial state looks like the days of the current month.
It is possible to switch to the state for choosing the month of the current year or in the state of choosing years.


.. literalinclude:: ./example.py

.. image::  /resources/calendar_days.png
.. image::  /resources/calendar_months.png
.. image::  /resources/calendar_years.png


Customization
==================

Providing :class:`calendar config <aiogram_dialog.widgets.kbd.CalendarConfig>` during calendar :meth:`initialization <aiogram_dialog.widgets.kbd.Calendar.__init__>` you can change basic params like minimal/maximal selected date or number of columns.

For deeper customization you need to inherit calendar and overload some methods.
In :meth:`_init_views <aiogram_dialog.widgets.kbd.Calendar_init_views>` you can create instances of built-in classes or create you own implementations. If using existing ones you can provide text widgets to customize representation of each button.

While rendering text the ``date`` field can be used to render text, and ``data`` is original data retrieved from window getter. For more details refer to source code.

.. note:: Though calendar supports setting timezone and first day of the week it doesn't translate any dates. If you want localized month or week day names you should provide your own ``Text`` widget with support of that.

For example, if you want to change first day of the week to Sunday, replace days view header and show today's button as ``***`` the code will look like this:


.. literalinclude:: ./custom.py
.. image::  /resources/calendar_custom.png

Classes
===========

.. autoclass:: aiogram_dialog.widgets.kbd.calendar_kbd.OnDateSelected
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.kbd.Calendar
   :members: _get_user_config, _init_views
   :special-members: __init__,

.. autoclass:: aiogram_dialog.widgets.kbd.ManagedCalendarAdapter
   :members: set_scope, set_offset, get_offset, get_scope

.. autoclass:: aiogram_dialog.widgets.kbd.CalendarUserConfig

.. autoclass:: aiogram_dialog.widgets.kbd.CalendarConfig

.. autoclass:: aiogram_dialog.widgets.kbd.calendar_kbd.CalendarScopeView
   :members: render

