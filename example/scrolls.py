import asyncio
import calendar
import logging
import os.path
from operator import itemgetter

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.widgets.kbd import (
    CurrentPage,
    FirstPage,
    LastPage,
    Multiselect,
    NextPage,
    NumberedPager,
    PrevPage,
    Row,
    ScrollingGroup,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, List, ScrollingText


class DialogSG(StatesGroup):
    MAIN = State()
    DEFAULT_PAGER = State()
    PAGERS = State()
    LIST = State()
    TEXT = State()
    STUB = State()


VERY_LONG_TEXT = """\
Lorem ipsum dolor sit amet. Ex dolores porro ut praesentium necessitatibus qui internos libero ut ipsa voluptatum eum blanditiis consequatur. Aut facere internos et nisi Quis eos omnis cumque. Et deleniti reprehenderit est aspernatur nulla ut impedit praesentium quo amet animi?

Id aperiam doloribus et quasi dolorem qui sunt consequatur non magni praesentium sed possimus omnis ut dolor natus est voluptatem dicta. In iure corporis non suscipit tempore qui veniam expedita et dolorem perferendis. Est autem blanditiis aut eius maxime in dolorem provident et veniam asperiores ea maxime rerum At nostrum temporibus! Aut nesciunt voluptatem ut eius autem eum Quis voluptatem ut iusto voluptas sed illo consequuntur vel molestiae quod.

Quo illo atque et pariatur magnam aut consectetur totam. Nam galisum neque ad laborum omnis 33 officia impedit ab odio officia est necessitatibus iste? Et ratione nulla non voluptas sunt vel dolores explicabo a quae enim et autem velit rem tempora nemo. Ut accusantium omnis vel iusto eius sit tempore illum aut aliquid vitae et accusamus repellat aut ducimus temporibus et omnis voluptates.

Et neque sint aut eius inventore et iste rerum a natus aliquid et natus obcaecati. Et quibusdam quos non ullam cupiditate ea molestiae tempore. Non quia ipsum qui velit quae eos molestias consequatur et quod autem et voluptas dolores et possimus pariatur in porro galisum.

Est molestiae laudantium non ullam facilis aut earum voluptatum ad omnis aliquid sed officia perferendis eum dignissimos debitis! Ea eaque architecto non voluptate possimus et dolores quos 33 rerum enim aut dolorem perferendis.

Eum minus impedit ut distinctio magni qui cupiditate minus qui distinctio beatae ut debitis velit rem accusantium accusantium et exercitationem nihil. Qui cupiditate porro ut sunt nemo et voluptatem ipsum. Et cumque dolorum eum quae earum aut impedit quasi nam fugit assumenda ex sapiente doloribus! A dolore Quis est labore nihil aut voluptatem rerum ut Quis voluptatem.

Rem culpa dolorum sed odio animi id quia inventore et molestiae quas. Qui suscipit placeat sit rerum alias eos esse aliquam est voluptas animi.

Ea illo recusandae et nisi possimus eos sunt corporis. Et dolor inventore aut nisi minus ut ipsam voluptas sed omnis ullam eos itaque galisum est omnis odit et cupiditate magnam.

Eos corporis quos aut magnam iure sed dicta galisum qui labore commodi rem nostrum ducimus vel nihil quia ut iste voluptate. Ut praesentium sint vel necessitatibus explicabo est aliquam rerum et dolorum aspernatur non neque modi est iste quos. Qui magnam voluptatem qui repellendus dolores ad voluptates nihil. Qui neque repellat et laboriosam officiis et officia eveniet qui iste porro et cupiditate error ea molestiae harum et dolorem modi.

Aut quae vitae nam ullam ratione sed blanditiis nihil aut nobis explicabo ab consequuntur quia ut unde quisquam qui impedit sunt. Ex dicta eligendi sed omnis facilis sed laudantium quas a corrupti iste! Quo vitae culpa eum saepe praesentium ad autem internos non Quis quidem qui vitae fuga. Et quis dolorem id voluptatibus dolor non quas incidunt in internos reprehenderit eos deserunt quas aut ipsum molestiae et rerum maiores?

Eos nulla eligendi rem galisum vero ut odio molestiae. Sed nulla iste quo deleniti possimus et doloremque sint vel sunt fuga sit laborum autem et doloribus laboriosam. Ab quae distinctio in magni quod est Quis explicabo ut tenetur magni in neque eius et ullam dolor.

Ea reprehenderit sunt aut voluptas vitae non iure consequatur. Aut repudiandae expedita et nulla sunt eum quae maiores non amet voluptas sed explicabo cumque ut totam laborum.

Eum odit tenetur eum galisum accusamus aut nulla iusto qui eaque illum non voluptatem magni. Ut placeat facere ea voluptatem voluptatem quo quia cumque aut provident cupiditate qui fuga voluptatem. Ad libero voluptatem rem aliquid deserunt est consequuntur pariatur et sequi asperiores et nostrum assumenda. Nam quia voluptatem aut quidem velit At fugit voluptas sit dicta dolores quo ratione delectus nam consectetur temporibus.

Id soluta voluptates a dolor amet est tempore modi et obcaecati dolor aut quae omnis. Qui nihil accusamus aut enim odit et ratione galisum cum assumenda sequi quo asperiores rerum et similique veniam non cumque ratione. Et nobis inventore aut facilis consequatur et commodi placeat eos quasi commodi non quis eligendi sit magnam consequatur et obcaecati Quis! Et expedita distinctio qui dolorum odio ut omnis tempore eos deserunt aspernatur vel sequi facilis.
"""  # noqa: E501


async def product_getter(**_kwargs):
    return {
        "products": [(f"Product {i}", i) for i in range(1, 30)],
    }


async def paging_getter(dialog_manager: DialogManager, **_kwargs):
    current_page = await dialog_manager.find("stub_scroll").get_page()
    return {
        "pages": 7,
        "current_page": current_page + 1,
        "day": calendar.day_name[current_page],
    }


MAIN_MENU_BTN = SwitchTo(Const("Main menu"), id="main", state=DialogSG.MAIN)

dialog = Dialog(
    Window(
        Const("Scrolling variant demo. Please, select an option:"),
        SwitchTo(
            Const("Default Pager"),
            state=DialogSG.DEFAULT_PAGER,
            id="default",
        ),
        SwitchTo(Const("Pager options"), id="pagers", state=DialogSG.PAGERS),
        SwitchTo(Const("Text list scroll"), id="list", state=DialogSG.LIST),
        SwitchTo(Const("Text scroll"), id="text", state=DialogSG.TEXT),
        SwitchTo(Const("Stub: getter-based"), id="stub", state=DialogSG.STUB),
        state=DialogSG.MAIN,
    ),
    Window(
        Const("Scrolling group with default pager (legacy mode)"),
        ScrollingGroup(
            Multiselect(
                Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id="ms",
                items="products",
                item_id_getter=itemgetter(1),
            ),
            width=1,
            height=5,
            id="scroll_with_pager",
        ),
        MAIN_MENU_BTN,
        getter=product_getter,
        state=DialogSG.DEFAULT_PAGER,
    ),
    Window(
        Const("Scrolling group with external paging controls"),
        NumberedPager(
            scroll="scroll_no_pager",
            page_text=Format("{target_page1}\uFE0F\u20E3"),
            current_page_text=Format("{current_page1}"),
        ),
        NumberedPager(
            scroll="scroll_no_pager",
        ),
        ScrollingGroup(
            Multiselect(
                Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id="ms",
                items="products",
                item_id_getter=itemgetter(1),
            ),
            width=1,
            height=5,
            hide_pager=True,
            id="scroll_no_pager",
        ),
        Row(

            FirstPage(
                scroll="scroll_no_pager", text=Format("⏮️ {target_page1}"),
            ),
            PrevPage(
                scroll="scroll_no_pager", text=Format("◀️"),
            ),
            CurrentPage(
                scroll="scroll_no_pager", text=Format("{current_page1}"),
            ),
            NextPage(
                scroll="scroll_no_pager", text=Format("▶️"),
            ),
            LastPage(
                scroll="scroll_no_pager", text=Format("{target_page1} ⏭️"),
            ),
        ),
        Row(
            PrevPage(scroll="scroll_no_pager"),
            NextPage(scroll="scroll_no_pager"),
            MAIN_MENU_BTN,
        ),
        getter=product_getter,
        state=DialogSG.PAGERS,
    ),
    Window(
        Const("Text list scrolling:\n"),
        List(
            Format("{pos}. {item[0]}"),
            items="products",
            id="list_scroll",
            page_size=10,
        ),
        NumberedPager(
            scroll="list_scroll",
        ),
        MAIN_MENU_BTN,
        getter=product_getter,
        state=DialogSG.LIST,
    ),
    Window(
        Const("Text scrolling:\n"),
        ScrollingText(
            text=Const(VERY_LONG_TEXT),
            id="text_scroll",
            page_size=1000,
        ),
        NumberedPager(
            scroll="text_scroll",
        ),
        MAIN_MENU_BTN,
        state=DialogSG.TEXT,
    ),
    Window(
        Const("Stub Scroll. Getter is used to paginate\n"),
        Format("You are at page {current_page} of {pages}"),
        Format("Day by number is {day}"),
        StubScroll(id="stub_scroll", pages="pages"),
        NumberedPager(
            scroll="stub_scroll",
        ),
        MAIN_MENU_BTN,
        state=DialogSG.STUB,
        getter=paging_getter,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(DialogSG.MAIN, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=os.getenv("BOT_TOKEN"))

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.message.register(start, CommandStart())
    dp.include_router(dialog)
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
