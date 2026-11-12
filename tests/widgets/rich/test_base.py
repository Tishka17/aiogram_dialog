import pytest
from aiogram import F

from aiogram_dialog.api.entities import RichFormat, RichParams
from aiogram_dialog.widgets.rich import RichBlocks, RichHtml, RichMarkdown


@pytest.mark.asyncio
@pytest.mark.parametrize(("widget", "rich_format"), [
    (RichHtml, RichFormat.HTML),
    (RichMarkdown, RichFormat.MARKDOWN),
    (RichBlocks, RichFormat.BLOCKS),
])
async def test_render_rich_params(widget, rich_format, mock_manager):
    rich = widget(is_rtl=True)
    res = await rich.render_rich_params({}, mock_manager)
    assert res == RichParams(format=rich_format, is_rtl=True)


@pytest.mark.asyncio
async def test_render_rich_params_when(mock_manager):
    rich = RichHtml(when=F["rich"])
    res = await rich.render_rich_params({"rich": True}, mock_manager)
    assert res == RichParams(format=RichFormat.HTML)
    res = await rich.render_rich_params({}, mock_manager)
    assert res is None
