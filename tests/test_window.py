from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Bot
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Chat, Message, User

from aiogram_dialog import DialogManager, DialogProtocol, Window
from aiogram_dialog.api.entities import (
    EVENT_CONTEXT_KEY,
    EventContext,
    ShowMode,
    StartMode,
)
from aiogram_dialog.api.protocols import MessageManagerProtocol
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.link_preview import LinkPreview
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format


# Dummy state for testing
class TestStates(State):
    MAIN = "main"


@pytest.fixture
def mock_bot() -> Bot:
    return AsyncMock(spec=Bot)


@pytest.fixture
def mock_message_manager() -> MessageManagerProtocol:
    return AsyncMock(spec=MessageManagerProtocol)


@pytest.fixture
def mock_event_context(mock_bot: Bot) -> EventContext:
    return EventContext(
        bot=mock_bot,
        chat=Chat(id=123, type="private", title="Test Chat"),
        user=User(id=456, is_bot=False, first_name="Test"),
        thread_id=None,
        business_connection_id=None,
    )


@pytest.fixture
def mock_dialog_manager(
    mock_bot: Bot,
    mock_event_context: EventContext,
    mock_message_manager: MessageManagerProtocol,
) -> DialogManager:
    manager = AsyncMock(spec=DialogManager)
    manager.event = MagicMock(spec=Message)
    manager.event.from_user = User(id=1, is_bot=False, first_name="User")
    manager.event.chat = Chat(id=1, type="private", title="User Chat")
    manager.bot = mock_bot
    manager.middleware_data = {
        "event_chat": Chat(id=123, type="private", title="Event Chat"),
        EVENT_CONTEXT_KEY: mock_event_context,
        "message_manager": mock_message_manager,
        "bot": mock_bot,
    }
    # Mock current_context() method to return an object with an .id attribute
    mock_context_obj = MagicMock()
    mock_context_obj.id = "test_context_id"
    mock_context_obj.state = TestStates.MAIN  # Dialogs might access this too
    mock_context_obj.start_data = {}
    mock_context_obj.dialog_data = {}
    # manager.current_context = AsyncMock(return_value=mock_context_obj)
    manager.current_context = MagicMock(
        return_value=mock_context_obj,
    )  # Changed to MagicMock (sync)

    manager.show_mode = ShowMode.EDIT
    manager.start_mode = StartMode.NORMAL
    manager.is_preview = MagicMock(return_value=False)
    return manager


@pytest.fixture
def mock_dialog_protocol() -> DialogProtocol:
    protocol = AsyncMock(spec=DialogProtocol)
    protocol.load_data = AsyncMock(return_value={})
    return protocol


@pytest.mark.asyncio
async def test_render_single_message_no_slots(
    mock_dialog_manager,
    mock_dialog_protocol,
):
    window = Window(
        Const("Hello"),
        state=TestStates.MAIN,
    )
    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 1
    msg = results[0]
    assert msg.text == "Hello"
    assert msg.reply_markup is None  # No keyboard
    assert msg.media is None


@pytest.mark.asyncio
async def test_render_with_one_slot(mock_dialog_manager, mock_dialog_protocol):
    window = Window(
        Const("Primary text"),
        slots=[
            [Const("Slot 1 text")],
        ],
        state=TestStates.MAIN,
    )
    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 2

    primary_msg = results[0]
    assert primary_msg.text == "Primary text"

    slot_msg = results[1]
    assert slot_msg.text == "Slot 1 text"


@pytest.mark.asyncio
async def test_render_with_multiple_slots(mock_dialog_manager, mock_dialog_protocol):
    window = Window(
        Const("Primary"),
        slots=[
            [Const("Slot 1")],
            [Const("Slot 2"), StaticMedia(url=Const("http://slot2.img"))],
            [Button(Const("Slot 3 Btn"), id="s3b")],
        ],
        state=TestStates.MAIN,
    )
    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 4
    assert results[0].text == "Primary"
    assert results[1].text == "Slot 1"
    assert results[2].text == "Slot 2"
    assert results[2].media is not None, "Media for slot 2 should not be None"
    assert results[2].media.url == "http://slot2.img"
    assert results[3].reply_markup is not None  # Keyboard for Slot 3 Btn


@pytest.mark.asyncio
async def test_render_slot_only_text(mock_dialog_manager, mock_dialog_protocol):
    window = Window(
        Const("P"),
        slots=[[Const("Slot Text Only")]],
        state=TestStates.MAIN,
    )
    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 2
    assert results[1].text == "Slot Text Only"
    assert results[1].media is None
    assert results[1].reply_markup is None


@pytest.mark.asyncio
async def test_render_slot_with_media_and_keyboard(
    mock_dialog_manager,
    mock_dialog_protocol,
):
    window = Window(
        Const("P"),
        slots=[
            [
                Const("Slot MK"),
                StaticMedia(url=Const("http://slot.mk")),
                Button(Const("Btn"), id="b1"),
            ],
        ],
        state=TestStates.MAIN,
    )
    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 2
    slot_msg = results[1]
    assert slot_msg.text == "Slot MK"
    assert slot_msg.media is not None
    assert slot_msg.media.url == "http://slot.mk"
    assert slot_msg.reply_markup is not None
    # Basic check for button presence, structure depends on MarkupFactory
    assert "Btn" in str(slot_msg.reply_markup)


@pytest.mark.asyncio
async def test_parse_mode_applies_to_all_messages(
    mock_dialog_manager,
    mock_dialog_protocol,
):
    window = Window(
        Const("Primary MD"),
        slots=[[Const("Slot MD")]],
        state=TestStates.MAIN,
        parse_mode="MarkdownV2",
    )
    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 2
    assert results[0].parse_mode == "MarkdownV2"
    assert results[1].parse_mode == "MarkdownV2"


@pytest.mark.asyncio
async def test_link_preview_behavior(mock_dialog_manager, mock_dialog_protocol):
    # 1. Deprecated disable_web_page_preview for primary
    window1 = Window(
        Const("Primary link preview test1"),
        state=TestStates.MAIN,
        disable_web_page_preview=True,
    )
    results1 = await window1.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results1) == 1
    assert results1[0].link_preview_options is not None
    assert results1[0].link_preview_options.is_disabled is True

    # 2. LinkPreview widget on primary message
    window2 = Window(
        Const("Primary link preview test2"),
        LinkPreview(url=Const("http://example.com/primary"), prefer_small_media=True),
        state=TestStates.MAIN,
    )
    results2 = await window2.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results2) == 1
    assert results2[0].link_preview_options is not None
    assert results2[0].link_preview_options.url == "http://example.com/primary"
    assert results2[0].link_preview_options.prefer_small_media is True

    # 3. LinkPreview widget on a slotted message, independent of primary
    window3 = Window(
        Const("Primary link preview test3"),
        slots=[
            [
                Const("Slot with link preview"),
                LinkPreview(is_disabled=True),
            ],
        ],
        state=TestStates.MAIN,
        disable_web_page_preview=False,  # Should not affect slot's explicit LinkPreview
    )
    results3 = await window3.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results3) == 2
    assert (
        results3[0].link_preview_options is None
    )  # No global disable, no widget for primary
    assert results3[1].link_preview_options is not None
    assert results3[1].link_preview_options.is_disabled is True

    # 4. Window-level disable_web_page_preview with explicit LinkPreview on primary (should raise ValueError)
    with pytest.raises(ValueError):
        Window(
            Const("Primary"),
            LinkPreview(url=Const("http://example.com")),
            state=TestStates.MAIN,
            disable_web_page_preview=True,
        )


@pytest.mark.asyncio
async def test_process_callback_primary_keyboard(
    mock_dialog_manager,
    mock_dialog_protocol,
):
    button_callback_mock = AsyncMock(return_value=True)
    window = Window(
        Const("P"),
        Button(Const("Btn1"), id="b1", on_click=button_callback_mock),
        state=TestStates.MAIN,
    )

    # Simulate a callback query for b1
    mock_callback_query = MagicMock(spec=CallbackQuery)
    mock_callback_query.data = "b1"
    mock_callback_query.message = MagicMock(spec=Message)
    mock_dialog_manager.event = mock_callback_query

    # Mock the process_callback of the Keyboard widget itself
    if window.keyboard:
        window.keyboard.process_callback = AsyncMock(return_value=True)

    handled = await window.process_callback(
        mock_callback_query,
        mock_dialog_protocol,
        mock_dialog_manager,
    )
    assert handled is True
    if window.keyboard:
        window.keyboard.process_callback.assert_called_once_with(
            mock_callback_query,
            mock_dialog_protocol,
            mock_dialog_manager,
        )


@pytest.mark.asyncio
async def test_process_callback_slot_keyboard(
    mock_dialog_manager,
    mock_dialog_protocol,
):
    slot_button_mock = AsyncMock(return_value=True)
    window = Window(
        Const("P"),
        slots=[
            [Button(Const("SlotBtn"), id="sb1", on_click=slot_button_mock)],
        ],
        state=TestStates.MAIN,
    )

    mock_callback_query = MagicMock(spec=CallbackQuery)
    mock_callback_query.data = "sb1"
    mock_callback_query.message = MagicMock(spec=Message)
    mock_dialog_manager.event = mock_callback_query

    # Mock the process_callback of the slot's Keyboard widget
    slot_keyboard_widget = window.slot_definitions[0]["keyboard"]
    assert slot_keyboard_widget is not None, "Slot keyboard widget should exist"

    slot_keyboard_widget.process_callback = AsyncMock(return_value=True)

    handled = await window.process_callback(
        mock_callback_query,
        mock_dialog_protocol,
        mock_dialog_manager,
    )
    assert handled is True
    slot_keyboard_widget.process_callback.assert_called_once_with(
        mock_callback_query,
        mock_dialog_protocol,
        mock_dialog_manager,
    )


@pytest.mark.asyncio
async def test_process_callback_no_handler(mock_dialog_manager, mock_dialog_protocol):
    window = Window(
        Const("P"),
        Button(Const("Btn1"), id="b1"),  # No on_click
        slots=[
            [Button(Const("SlotBtn"), id="sb1")],  # No on_click
        ],
        state=TestStates.MAIN,
    )

    mock_callback_query = MagicMock(spec=CallbackQuery)
    mock_callback_query.data = "unknown_button"
    mock_callback_query.message = MagicMock(spec=Message)
    mock_dialog_manager.event = mock_callback_query

    if window.keyboard:
        window.keyboard.process_callback = AsyncMock(return_value=False)

    if window.slot_definitions and window.slot_definitions[0]["keyboard"]:
        window.slot_definitions[0]["keyboard"].process_callback = AsyncMock(
            return_value=False,
        )

    handled = await window.process_callback(
        mock_callback_query,
        mock_dialog_protocol,
        mock_dialog_manager,
    )
    assert handled is False


@pytest.mark.asyncio
async def test_find_widget_primary(mock_dialog_manager, mock_dialog_protocol):
    target_button = Button(Const("Btn Target"), id="target_btn")
    window = Window(
        Const("P"),
        target_button,
        state=TestStates.MAIN,
    )
    found_widget = window.find("target_btn")
    assert found_widget is target_button


@pytest.mark.asyncio
async def test_find_widget_slot(mock_dialog_manager, mock_dialog_protocol):
    slot_target_button = Button(Const("Slot Target"), id="slot_target_btn")
    window = Window(
        Const("P"),
        slots=[
            [Const("Slot Text"), slot_target_button],
        ],
        state=TestStates.MAIN,
    )
    found_widget = window.find("slot_target_btn")
    assert found_widget is slot_target_button


@pytest.mark.asyncio
async def test_find_widget_not_found(mock_dialog_manager, mock_dialog_protocol):
    window = Window(
        Const("P"),
        Button(Const("Btn"), id="b1"),
        slots=[[Const("Slot Text")]],
        state=TestStates.MAIN,
    )
    found_widget = window.find("non_existent_widget")
    assert found_widget is None


@pytest.mark.asyncio
async def test_on_message_handler_primary(mock_dialog_manager, mock_dialog_protocol):
    message_handler_mock = AsyncMock()
    message_input_widget = MessageInput(message_handler_mock)
    message_input_widget.process_message = AsyncMock(return_value=True)

    window = Window(
        message_input_widget,
        state=TestStates.MAIN,
    )

    test_message = MagicMock(spec=Message)
    test_message.text = "Hello world"

    handled = await window.process_message(
        test_message,
        mock_dialog_protocol,
        mock_dialog_manager,
    )

    assert handled is True
    message_input_widget.process_message.assert_called_once_with(
        test_message,
        mock_dialog_protocol,
        mock_dialog_manager,
    )


@pytest.mark.asyncio
async def test_on_message_handler_slot_not_processed(
    mock_dialog_manager,
    mock_dialog_protocol,
):
    primary_handler_mock = AsyncMock()
    slot_handler_mock = AsyncMock()

    primary_message_input = MessageInput(primary_handler_mock)
    primary_message_input.process_message = AsyncMock(return_value=True)

    slot_message_input = MessageInput(slot_handler_mock)
    slot_message_input.process_message = AsyncMock(return_value=False)

    window = Window(
        primary_message_input,
        slots=[
            [slot_message_input],
        ],
        state=TestStates.MAIN,
    )

    test_message = MagicMock(spec=Message)

    handled = await window.process_message(
        test_message,
        mock_dialog_protocol,
        mock_dialog_manager,
    )

    assert handled is True
    primary_message_input.process_message.assert_called_once()
    slot_message_input.process_message.assert_not_called()


@pytest.mark.asyncio
async def test_empty_slots_list(mock_dialog_manager, mock_dialog_protocol):
    window = Window(
        Const("Primary with empty slots"),
        slots=[],  # Empty list
        state=TestStates.MAIN,
    )
    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 1
    assert results[0].text == "Primary with empty slots"


@pytest.mark.asyncio
async def test_getter_data_accessible_in_all_renders(
    mock_dialog_manager,
    mock_dialog_protocol,
):
    async def test_getter(dialog_manager, **kwargs):
        return {"name": "Tester", "item_count": 5}

    mock_dialog_protocol.load_data = AsyncMock(return_value={"initial_data": "exists"})

    window = Window(
        Format("Primary: {name} has {item_count} items. Initial: {initial_data}"),
        slots=[
            [Format("Slot1: {name}, items: {item_count}. Initial: {initial_data}")],
            [Format("Slot2: Hello, {name}! Initial: {initial_data}")],
        ],
        state=TestStates.MAIN,
        getter=test_getter,
    )

    results = await window.render(mock_dialog_protocol, mock_dialog_manager)
    assert len(results) == 3

    assert results[0].text == "Primary: Tester has 5 items. Initial: exists"
    assert results[1].text == "Slot1: Tester, items: 5. Initial: exists"
    assert results[2].text == "Slot2: Hello, Tester! Initial: exists"

    mock_dialog_protocol.load_data.assert_called_once_with(mock_dialog_manager)
