.. _calendar:

Calendar
*************

**Calendar** widget allows you to display the keyboard in the form of a calendar, flip through the months and select the date.
The initial state looks like the days of the current month.
It is possible to switch to the state for choosing the month of the current year or in the state of choosing years.

.. literalinclude:: ./example.py

.. image::  /resources/calendar1.png
.. image::  /resources/calendar2.png
.. image::  /resources/calendar3.png

.. autoclass:: aiogram_dialog.widgets.kbd.calendar_kbd.OnDateSelected
   :special-members: __call__

.. autoclass:: aiogram_dialog.widgets.kbd.Calendar
   :members: _get_config, _init_views
   :special-members: __init__,

.. autoclass:: aiogram_dialog.widgets.kbd.ManagedCalendarAdapter
   :members: set_scope, set_offset, get_offset, get_scope

.. autoclass:: aiogram_dialog.widgets.kbd.CalendarUserConfig

.. autoclass:: aiogram_dialog.widgets.kbd.CalendarConfig

.. autoclass:: aiogram_dialog.widgets.kbd.calendar_kbd.CalendarScopeView
   :members: render

