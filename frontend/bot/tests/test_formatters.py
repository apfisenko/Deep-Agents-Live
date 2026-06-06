"""Formatter tests."""

from formatters import escape_html, markdown_to_telegram_html


def test_bold_markdown() -> None:
    result = markdown_to_telegram_html("**важно**")
    assert result == "<b>важно</b>"


def test_link_markdown() -> None:
    result = markdown_to_telegram_html("[оплата](https://pay.mock.llmstart.ru/order-1)")
    assert '<a href="https://pay.mock.llmstart.ru/order-1">оплата</a>' in result


def test_escape_html_specials() -> None:
    assert escape_html("a < b & c") == "a &lt; b &amp; c"
