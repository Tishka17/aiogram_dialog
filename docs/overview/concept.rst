.. _concept:
Concept
*************

Aiogram-dialog is a GUI framework for telegram bot. It is inspired by ideas of Android SDK and React.js

Main ideas are:

1. Split data retrieving and message rendering
2. Unite rendering buttons and processing clicks
3. Better states routing
4. Widgets

The main building block of your UI is **Window**. Each window represents a message sent to user and processing of a user reaction on it.

Each window consists of **Widgets** and callback functions. Widgets can represent message text and keyboard. Callbacks are used to retrieve required data or process user input.

You combine windows into **Dialog**. This allows you to switch between windows creating different scenarios of communication with user.

In more complex cases you can create more than one dialog. Then you can start new dialogs without closing previous one and automatically return back when it is closed. You can pass data between dialogs keeping they state isolated at the same time.
