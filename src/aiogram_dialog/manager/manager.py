import sys
from copy import deepcopy
from logging import getLogger
from typing import Any, Optional, Union, cast

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Chat, Message, ReplyKeyboardMarkup, User

from aiogram_dialog.api.entities import (
    DEFAULT_STACK_ID,
    EVENT_CONTEXT_KEY,
    AccessSettings,
    ChatEvent,
    Context,
    Data,
    EventContext,
    LaunchMode,
    MediaId,
    NewMessage,
    OldMessage,
    ShowMode,
    Stack,
    StartMode,
    UnknownText,
)
from aiogram_dialog.api.exceptions import (
    IncorrectBackgroundError,
    InvalidKeyboardType,
    NoContextError,
)
from aiogram_dialog.api.internal import (
    CONTEXT_KEY,
    EVENT_SIMULATED,
    STACK_KEY,
    STORAGE_KEY,
    FakeChat,
    FakeUser,
)
from aiogram_dialog.api.protocols import (
    BaseDialogManager,
    DialogManager,
    DialogProtocol,
    DialogRegistryProtocol,
    MediaIdStorageProtocol,
    MessageManagerProtocol,
    MessageNotModified,
    UnsetId,
)
from aiogram_dialog.context.storage import StorageProxy
from aiogram_dialog.utils import get_media_id

from .bg_manager import BgManager, coalesce_business_connection_id, coalesce_thread_id

logger = getLogger(__name__)


class ManagerImpl(DialogManager):

    def __init__(
        self,
        event: ChatEvent,
        message_manager: MessageManagerProtocol,
        media_id_storage: MediaIdStorageProtocol,
        registry: DialogRegistryProtocol,
        router: Router,
        data: dict,
    ):
        self.disabled = False
        self.message_manager = message_manager
        self.media_id_storage = media_id_storage
        self._event = event
        self._data = data
        self._show_mode: ShowMode = ShowMode.AUTO
        self._registry = registry
        self._router = router

    @property
    def show_mode(self) -> ShowMode:
        """Get current show mode, used for next show action."""
        return self._show_mode

    @show_mode.setter
    def show_mode(self, show_mode: ShowMode) -> None:
        """Set current show mode, used for next show action."""
        self._show_mode = show_mode

    @property
    def event(self) -> ChatEvent:
        return self._event

    @property
    def middleware_data(self) -> dict:
        """Middleware data."""
        return self._data

    @property
    def dialog_data(self) -> dict:
        """Dialog data for current context."""
        return self.current_context().dialog_data

    @property
    def start_data(self) -> Data:
        """Start data for current context."""
        return self.current_context().start_data

    def check_disabled(self):
        if self.disabled:
            raise IncorrectBackgroundError(
                "Detected background access to dialog manager. "
                "Please use background manager available via `manager.bg()` "
                "method to access methods from background tasks",
            )

    async def load_data(self) -> dict:
        context = self.current_context()
        return {
            "dialog_data": context.dialog_data,
            "start_data": context.start_data,
            "middleware_data": self._data,
            "event": self.event,
        }

    def is_preview(self) -> bool:
        return False

    def dialog(self) -> DialogProtocol:
        self.check_disabled()
        current = self.current_context()
        if not current:
            raise RuntimeError
        return self._registry.find_dialog(current.state)

    def current_context(self) -> Context:
        self.check_disabled()
        context = self._current_context_unsafe()
        if not context:
            logger.warning(
                "Trying to access current context, while no dialog is opened",
            )
            raise NoContextError
        return context

    def _current_context_unsafe(self) -> Optional[Context]:
        return self._data[CONTEXT_KEY]

    def has_context(self) -> bool:
        self.check_disabled()
        return bool(self._current_context_unsafe())

    def current_stack(self) -> Stack:
        self.check_disabled()
        return self._data[STACK_KEY]

    def storage(self) -> StorageProxy:
        return self._data[STORAGE_KEY]

    async def _delete_all_stack_messages(self) -> None:
        self.check_disabled()
        stack = self.current_stack()
        if not stack.sent_messages:
            return
        bot = self._data["bot"]

        messages_to_delete = list(stack.sent_messages)
        # Clear the list in the stack representation first.
        # If actual deletion fails, the messages are gone from our POV.
        stack.sent_messages.clear()

        for old_message_obj in messages_to_delete:
            try:
                # Use remove_kbd with DELETE_AND_SEND to trigger deletion via protocol
                await self.message_manager.remove_kbd(
                    bot=bot,
                    old_message=old_message_obj,
                    show_mode=ShowMode.DELETE_AND_SEND,
                )
            except Exception as e:
                logger.warning(
                    "Failed to delete message %s in chat %s via remove_kbd: %s",
                    old_message_obj.message_id,
                    old_message_obj.chat.id,
                    e,
                )

    async def _process_last_dialog_result(
        self,
        start_data: Data,
        result: Any,
    ) -> None:
        """Process closing last dialog in stack."""
        await self._delete_all_stack_messages()

    async def done(
        self,
        result: Any = None,
        show_mode: Optional[ShowMode] = None,
    ) -> None:
        self.check_disabled()
        await self.dialog().process_close(result, self)
        old_context = self.current_context()
        await self.mark_closed()
        context = self._current_context_unsafe()
        if not context:
            await self._process_last_dialog_result(
                old_context.start_data,
                result,
            )
            return
        dialog = self.dialog()
        await dialog.process_result(old_context.start_data, result, self)
        new_context = self._current_context_unsafe()
        if new_context and context.id == new_context.id:
            await self.show(show_mode)

    async def answer_callback(self) -> None:
        if not isinstance(self.event, CallbackQuery):
            return None
        if self.is_event_simulated():
            return None
        return await self.message_manager.answer_callback(
            bot=self._data["bot"],
            callback_query=self.event,
        )

    async def mark_closed(self) -> None:
        self.check_disabled()
        storage = self.storage()
        stack = self.current_stack()
        await storage.remove_context(stack.pop())
        if stack.empty():
            self._data[CONTEXT_KEY] = None
        else:
            intent_id = stack.last_intent_id()
            self._data[CONTEXT_KEY] = await storage.load_context(intent_id)
        await storage.save_stack(stack)

    async def start(
        self,
        state: State,
        data: Data = None,
        mode: StartMode = StartMode.NORMAL,
        show_mode: Optional[ShowMode] = None,
        access_settings: Optional[AccessSettings] = None,
    ) -> None:
        self.check_disabled()
        self.show_mode = show_mode or self.show_mode
        if mode is StartMode.NORMAL:
            await self._start_normal(state, data, access_settings)
        elif mode is StartMode.RESET_STACK:
            await self.reset_stack(remove_keyboard=False)
            await self._start_normal(state, data, access_settings)
        elif mode is StartMode.NEW_STACK:
            await self._start_new_stack(state, data, access_settings)
        else:
            raise ValueError(f"Unknown start mode: {mode}")

    async def reset_stack(self, remove_keyboard: bool = True) -> None:
        self.check_disabled()
        storage = self.storage()
        stack = self.current_stack()
        if remove_keyboard:
            await self._delete_all_stack_messages()

        for intent_id in reversed(stack.intents):
            await storage.remove_context(intent_id)
        stack.intents.clear()
        await storage.save_stack(stack)
        self._data[CONTEXT_KEY] = None

    async def _start_new_stack(
        self,
        state: State,
        data: Data,
        access_settings: Optional[AccessSettings],
    ) -> None:
        stack = Stack()
        await self.bg(stack_id=stack.id).start(
            state,
            data,
            mode=StartMode.NORMAL,
            show_mode=self.show_mode,
            access_settings=access_settings,
        )

    async def _start_normal(
        self,
        state: State,
        data: Data,
        access_settings: Optional[AccessSettings],
    ) -> None:
        stack = self.current_stack()
        old_dialog: Optional[DialogProtocol] = None
        if not stack.empty():
            old_dialog = self.dialog()
            if old_dialog.launch_mode is LaunchMode.EXCLUSIVE:
                raise ValueError(
                    "Cannot start dialog on top of one with launch_mode==SINGLE",
                )

        new_dialog = self._registry.find_dialog(state)
        await self._process_launch_mode(old_dialog, new_dialog)
        if self.has_context():
            await self.storage().save_context(self.current_context())
            if access_settings is None:
                access_settings = self.current_context().access_settings
        if access_settings is None:
            access_settings = stack.access_settings

        context = stack.push(state, data)
        context.access_settings = deepcopy(access_settings)
        self._data[CONTEXT_KEY] = context
        await self.dialog().process_start(self, data, state)
        new_context = self._current_context_unsafe()
        if new_context and context.id == new_context.id:
            await self.show()

    async def _process_launch_mode(
        self,
        old_dialog: Optional[DialogProtocol],
        new_dialog: DialogProtocol,
    ):
        if new_dialog.launch_mode in (LaunchMode.EXCLUSIVE, LaunchMode.ROOT):
            await self.reset_stack(remove_keyboard=False)
        if new_dialog.launch_mode is LaunchMode.SINGLE_TOP:  # noqa: SIM102
            if new_dialog is old_dialog:
                await self.storage().remove_context(self.current_stack().pop())
                self._data[CONTEXT_KEY] = None

    async def next(self, show_mode: Optional[ShowMode] = None) -> None:
        context = self.current_context()
        states = self.dialog().states()
        current_index = states.index(context.state)
        new_state = states[current_index + 1]
        await self.switch_to(new_state, show_mode)

    async def back(self, show_mode: Optional[ShowMode] = None) -> None:
        context = self.current_context()
        states = self.dialog().states()
        current_index = states.index(context.state)
        new_state = states[current_index - 1]
        await self.switch_to(new_state, show_mode)

    async def switch_to(
        self,
        state: State,
        show_mode: Optional[ShowMode] = None,
    ) -> None:
        self.check_disabled()
        context = self.current_context()
        if context.state.group != state.group:
            raise ValueError(
                f"Cannot switch to another state group. "
                f"Current state: {context.state}, asked for {state}",
            )
        self.show_mode = show_mode or self.show_mode
        context.state = state

    def _ensure_stack_compatible(
        self,
        stack: Stack,
        new_message: NewMessage,
    ) -> None:
        if stack.id == DEFAULT_STACK_ID:
            return  # no limitations for default stack
        if isinstance(new_message.reply_markup, ReplyKeyboardMarkup):
            raise InvalidKeyboardType(
                "Cannot use ReplyKeyboardMarkup in non default stack",
            )

    async def show(self, show_mode: Optional[ShowMode] = None) -> None:
        try:
            current_stack = self.current_stack()
            bot = self._data["bot"]

            if (
                self.show_mode is ShowMode.NO_UPDATE and show_mode is None
            ):  # if show_mode is set directly, override NO_UPDATE
                logger.debug("ShowMode is NO_UPDATE, skip rendering")
                return

            new_messages_to_render = await self.dialog().render(self)

            # Determine effective show mode for this operation
            # Note: _calc_show_mode might need the first new_message to make a decision
            # For now, we'll calculate it once if possible, or per message if needed.
            # This example assumes _calc_show_mode is called per message later.
            # Let's simplify: calculate overall show_mode first.
            # If new_messages_to_render is empty, we might just want to delete.

            # Snapshot messages currently on stack and clear them from stack representation
            previous_sent_messages = list(current_stack.sent_messages)
            current_stack.sent_messages.clear()

            effective_overall_show_mode = show_mode or self.show_mode
            if effective_overall_show_mode == ShowMode.AUTO and new_messages_to_render:
                # Pass the first message to _calc_show_mode if it needs it
                effective_overall_show_mode = self._calc_show_mode(
                    ShowMode.AUTO,
                    new_messages_to_render[0],
                )
            elif (
                effective_overall_show_mode == ShowMode.AUTO
                and not new_messages_to_render
            ):
                # If no new messages, and AUTO, default to EDIT (which might mean no-op or clear if last dialog)
                # Or, if we want to ensure cleanup, consider DELETE_AND_SEND for empty render.
                # For now, let _process_last_dialog_result handle cleanup if stack becomes empty.
                effective_overall_show_mode = ShowMode.EDIT

            if not new_messages_to_render:
                if effective_overall_show_mode == ShowMode.DELETE_AND_SEND:
                    logger.debug(
                        "No new messages to render, deleting previous messages.",
                    )
                    for old_msg_obj in previous_sent_messages:
                        try:
                            await self.message_manager.remove_kbd(
                                bot=bot,
                                old_message=old_msg_obj,
                                show_mode=ShowMode.DELETE_AND_SEND,
                            )
                        except Exception as e:
                            logger.warning(
                                "Failed to delete message %s: %s",
                                old_msg_obj.message_id,
                                e,
                            )
                # else: if not DELETE_AND_SEND and no new messages, effectively do nothing with old messages here.
                # They were cleared from stack.sent_messages, but not deleted from chat unless mode dictated.
                # This might leave messages on screen if transitioning from a window with messages to one with none
                # without DELETE_AND_SEND. This is complex. For now, focus on DELETE_AND_SEND.
                await self.storage().save_stack(
                    current_stack,
                )  # Save cleared sent_messages
                return

            # Handle deletion if mode is DELETE_AND_SEND
            if effective_overall_show_mode == ShowMode.DELETE_AND_SEND:
                logger.debug(
                    "Effective mode is DELETE_AND_SEND, deleting %d previous messages.",
                    len(previous_sent_messages),
                )
                for old_msg_obj in previous_sent_messages:
                    try:
                        await self.message_manager.remove_kbd(
                            bot=bot,
                            old_message=old_msg_obj,
                            show_mode=ShowMode.DELETE_AND_SEND,
                        )
                    except Exception as e:
                        logger.warning(
                            "Failed to delete message %s: %s",
                            old_msg_obj.message_id,
                            e,
                        )
                # previous_sent_messages are now deleted from chat, no need to pass them as old_message for edit

            last_actually_sent_or_edited_message: Optional[OldMessage] = None

            for idx, current_new_msg_spec in enumerate(new_messages_to_render):
                # Each new message spec needs its own show_mode if AUTO was resolved per message
                # For now, we use effective_overall_show_mode for all parts of a multi-message window.
                current_new_msg_spec.show_mode = effective_overall_show_mode

                await self._fix_cached_media_id(current_new_msg_spec)

                message_to_pass_as_old = None
                if (
                    idx == 0
                    and effective_overall_show_mode != ShowMode.DELETE_AND_SEND
                    and previous_sent_messages
                ):
                    # If not deleting all, and it's the first new message,
                    # pass the last of the *previous* screen's messages for potential edit.
                    message_to_pass_as_old = previous_sent_messages[-1]

                # If effective_overall_show_mode was DELETE_AND_SEND, message_to_pass_as_old should remain None.

                try:
                    sent_or_edited_msg_obj = await self.message_manager.show_message(
                        bot=bot,
                        new_message=current_new_msg_spec,
                        old_message=message_to_pass_as_old,
                    )
                    self._save_last_message(
                        sent_or_edited_msg_obj,
                    )  # Appends to current_stack.sent_messages
                    last_actually_sent_or_edited_message = sent_or_edited_msg_obj

                    if current_new_msg_spec.media:  # Save media ID if applicable
                        await self.media_id_storage.save_media_id(
                            path=current_new_msg_spec.media.path,
                            url=current_new_msg_spec.media.url,
                            type=current_new_msg_spec.media.type,
                            media_id=MediaId(
                                file_id=sent_or_edited_msg_obj.media_id,
                                file_unique_id=sent_or_edited_msg_obj.media_uniq_id,
                            ),
                        )
                except MessageNotModified:
                    logger.debug(
                        "Message %d of %d did not change.",
                        idx + 1,
                        len(new_messages_to_render),
                    )
                    if (
                        message_to_pass_as_old
                    ):  # If it was an edit attempt that resulted in no change
                        self._save_last_message(
                            message_to_pass_as_old,
                        )  # Re-add the old message to the new stack state
                        last_actually_sent_or_edited_message = message_to_pass_as_old
                except Exception:
                    logger.exception(
                        "Failed to show message %d of %d.",
                        idx + 1,
                        len(new_messages_to_render),
                    )
                    # If one part of a multi-message window fails, what to do?
                    # For now, we re-raise. Consider rollback or cleanup of messages already sent in this batch.
                    raise

            # Save stack after all messages in the window are processed
            await self.storage().save_stack(current_stack)

            if isinstance(self.event, Message) and last_actually_sent_or_edited_message:
                # This was for media group optimization, might need rethinking with multiple messages
                current_stack.last_income_media_group_id = self.event.media_group_id
                await self.storage().save_stack(current_stack)

        except (
            MessageNotModified
        ):  # This outer one catches if the whole dialog.render was NO_UPDATE
            logger.debug("Overall window show resulted in NO_UPDATE or no net change.")
            # If stack.sent_messages was cleared but nothing new was added due to NO_UPDATE,
            # we might need to restore previous_sent_messages to the stack.
            # current_stack.sent_messages.extend(previous_sent_messages) # Example, needs careful thought
            await self.storage().save_stack(
                current_stack,
            )  # Save potentially modified stack (e.g. cleared messages)
        except Exception as e:
            if sys.version_info >= (3, 11) and self.has_context():
                try:
                    current_context_state = self.current_context().state
                    e.add_note(f"aiogram-dialog state: {current_context_state}")
                except NoContextError:
                    e.add_note("aiogram-dialog state: NoContextError")
            raise

    async def _fix_cached_media_id(self, new_message: NewMessage):
        if not new_message.media or new_message.media.file_id:
            return
        new_message.media.file_id = await self.media_id_storage.get_media_id(
            path=new_message.media.path,
            url=new_message.media.url,
            type=new_message.media.type,
        )

    def is_event_simulated(self):
        return bool(self.middleware_data.get(EVENT_SIMULATED))

    def _get_message_from_callback(
        self,
        event: CallbackQuery,
    ) -> Optional[OldMessage]:
        if not event.message:
            return None
        if event.message.content_type == ContentType.UNKNOWN:
            # Bug in TG. message is not accessible
            # event.message.text is None, even if it is a text
            return UnknownText(
                message_id=event.message.message_id,
                chat=event.message.chat,
                business_connection_id=event.message.business_connection_id,
            )
        media_id = get_media_id(event.message)
        return OldMessage(
            message_id=event.message.message_id,
            chat=event.message.chat,
            has_reply_keyboard=isinstance(
                event.message.reply_markup,
                ReplyKeyboardMarkup,
            ),
            text=event.message.text,
            media_uniq_id=(media_id.file_unique_id if media_id else None),
            media_id=(media_id.file_id if media_id else None),
            business_connection_id=event.message.business_connection_id,
            content_type=event.message.content_type,
        )

    def _get_last_message(self) -> Optional[OldMessage]:
        self.check_disabled()
        stack = self._data.get(STACK_KEY)
        if not stack or not stack.sent_messages:  # Changed to check stack.sent_messages
            return None
        return stack.sent_messages[-1]  # Return the last OldMessage object

    def _save_last_message(self, message: OldMessage) -> None:
        self.check_disabled()
        stack = self.current_stack()
        stack.sent_messages.append(message)  # Append OldMessage object

    def _calc_show_mode(
        self,
        show_mode: Optional[ShowMode],
        new_message: NewMessage,
    ) -> ShowMode:
        if show_mode is not ShowMode.AUTO:
            return show_mode

        current_stack = self.current_stack()
        event_chat_type = self.middleware_data["event_chat"].type

        if event_chat_type != ChatType.PRIVATE:
            return ShowMode.EDIT

        # Check if the last sent message (if any) had a reply keyboard
        had_reply_keyboard_on_last_message = False
        if current_stack.sent_messages:
            had_reply_keyboard_on_last_message = current_stack.sent_messages[
                -1
            ].has_reply_keyboard

        if had_reply_keyboard_on_last_message:
            return ShowMode.DELETE_AND_SEND

        if current_stack.id != DEFAULT_STACK_ID:
            return ShowMode.EDIT

        if isinstance(self.event, Message):
            if self.event.media_group_id is None:
                return ShowMode.SEND
            elif self.event.media_group_id == current_stack.last_income_media_group_id:
                return ShowMode.EDIT
            else:
                return ShowMode.SEND
        return ShowMode.EDIT

    async def update(
        self,
        data: dict,
        show_mode: Optional[ShowMode] = None,
    ) -> None:
        self.current_context().dialog_data.update(data)
        await self.show(show_mode)

    def find(self, widget_id) -> Optional[Any]:
        widget = self.dialog().find(widget_id)
        if not widget:
            return None
        return widget.managed(self)

    def _get_fake_user(self, user_id: Optional[int] = None) -> User:
        """Get User if we have info about him or FakeUser instead."""
        current_user = self.event.from_user
        if user_id in (None, current_user.id):
            return current_user
        return FakeUser(id=user_id, is_bot=False, first_name="")

    def _get_fake_chat(self, chat_id: Optional[int] = None) -> Chat:
        """Get Chat if we have info about him or FakeChat instead."""
        if "event_chat" in self._data:
            current_chat = self._data["event_chat"]
            if chat_id in (None, current_chat.id):
                return current_chat
        elif chat_id is None:
            raise ValueError(
                "Explicit `chat_id` is required for events without current chat",
            )
        return FakeChat(id=chat_id, type="")

    def bg(
        self,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        stack_id: Optional[str] = None,
        thread_id: Union[int, None, UnsetId] = UnsetId.UNSET,
        business_connection_id: Union[str, None, UnsetId] = UnsetId.UNSET,
        load: bool = False,
    ) -> BaseDialogManager:
        user = self._get_fake_user(user_id)
        chat = self._get_fake_chat(chat_id)
        intent_id = None
        event_context = cast(
            "EventContext",
            self.middleware_data.get(EVENT_CONTEXT_KEY),
        )
        new_event_context = EventContext(
            bot=event_context.bot,
            chat=chat,
            user=user,
            thread_id=coalesce_thread_id(
                chat=chat,
                user=user,
                thread_id=thread_id,
                event_context=event_context,
            ),
            business_connection_id=coalesce_business_connection_id(
                chat=chat,
                user=user,
                business_connection_id=business_connection_id,
                event_context=event_context,
            ),
        )

        if stack_id is None:
            if event_context == new_event_context:
                stack_id = self.current_stack().id
                if self.has_context():
                    intent_id = self.current_context().id
            else:
                stack_id = DEFAULT_STACK_ID

        return BgManager(
            user=new_event_context.user,
            chat=new_event_context.chat,
            bot=new_event_context.bot,
            router=self._router,
            intent_id=intent_id,
            stack_id=stack_id,
            thread_id=new_event_context.thread_id,
            business_connection_id=new_event_context.business_connection_id,
            load=load,
        )

    async def close_manager(self) -> None:
        self.check_disabled()
        self.disabled = True
        del self.media_id_storage
        del self.message_manager
        del self._event
        del self._data
