import pytest
from aiogram import F
from aiogram.enums import ButtonStyle

from aiogram_dialog.widgets.style import Style


@pytest.mark.asyncio
async def test_or_condition_style(mock_manager):
    text = (
            Style(ButtonStyle.PRIMARY, when=F["a"]) |
            Style(ButtonStyle.SUCCESS, when=F["b"]) |
            Style(ButtonStyle.DANGER)
    )
    res = await text.render_style({"a": True}, mock_manager)
    assert res == ButtonStyle.PRIMARY
    res = await text.render_style({"b": True}, mock_manager)
    assert res == ButtonStyle.SUCCESS
    res = await text.render_style({}, mock_manager)
    assert res == ButtonStyle.DANGER


@pytest.mark.asyncio
async def test_or_condition_icon(mock_manager):
    text = (
            Style(emoji_id="a1", when=F["a"]) |
            Style(emoji_id="b2", when=F["b"]) |
            Style(emoji_id="c3")
    )
    res = await text.render_emoji({"a": True}, mock_manager)
    assert res == "a1"
    res = await text.render_emoji({"b": True}, mock_manager)
    assert res == "b2"
    res = await text.render_emoji({}, mock_manager)
    assert res == "c3"
