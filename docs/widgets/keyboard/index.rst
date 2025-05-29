.. _keyboard_widgets:

Keyboard widget types
*****************************

Each keyboard provides one or multiple inline buttons. Text on button is rendered using text widget

* :ref:`Button<button>` - single inline button. User provided ``on_click`` method is called when it is clicked.
* :ref:`Url<url>` - single inline button with url
* :ref:`LoginURLButton<login_url>` - a single inline button with HTTPS URL used to automatically authorize the user
* :ref:`SwitchInlineQuery<switch_inline_query>` - single inline button to switch inline mode
* :ref:`SwitchInlineQueryCurrentChat<switch_inline_query_current_chat>` - a single inline button that inserts the bot's username and specified inline query into the current chat's input field
* :ref:`SwitchInlineQueryChosenChatButton<switch_inline_query_chosen_chat>` - a single inline button that prompts the user to select one of their chats based on the specified scopes, opens the selected chat, and inserts the bot's username and the given inline query into the input field
* :ref:`Group<group>` - any group of keyboards one above another or rearranging buttons.
* :ref:`Row<row>` - simplified version of group. All buttons placed in single row.
* :ref:`Column<column>` - another simplified version of group. All buttons placed in single column one per row.
* :ref:`ScrollingGroup<scrolling_group>` - the same as the ``Group``, but with the ability to scroll through pages with buttons.
* :ref:`ListGroup<list_group>` - group of widgets applied repeated multiple times for each item in list
* :ref:`Checkbox<checkbox>` - button with two states
* :ref:`Select<select>` - dynamic group of buttons intended for selection use.
* :ref:`Radio<radio>` - switch between multiple items. Like select but stores chosen item and renders it differently.
* :ref:`Multiselect<multiselect>` - selection of multiple items. Like select/radio but stores all chosen items and renders them differently.
* :ref:`Toggle<toggle>` - to switch between elements of the list
* :ref:`Calendar<calendar>` - simulates a calendar in the form of a keyboard.
* :ref:`Counter<counter>` - couple of buttons +/- to input a number
* :ref:`SwitchTo<switch_to>` - switches window within a dialog using provided state
* :ref:`Next and Back<next_and_back>` - switches state forward or backward
* :ref:`Start<start>` - starts a new dialog with no params
* :ref:`Cancel<cancel>` - closes the current dialog with no result. An underlying dialog is shown
* :ref:`RequestPoll<request_poll>` - a single reply keyboard button that asks the user to create a poll and send it to the bot

.. toctree::
    :hidden:

    button/index
    url/index
    login_url/index
    switch_inline_query/index
    switch_inline_query_current_chat/index
    switch_inline_query_chosen_chat/index
    group/index
    column/index
    row/index
    list_group/index
    scrolling_group/index
    checkbox/index
    select/index
    radio/index
    multiselect/index
    toggle/index
    calendar/index
    counter/index
    switch_to/index
    next_and_back/index
    start/index
    cancel/index
    request_poll/index