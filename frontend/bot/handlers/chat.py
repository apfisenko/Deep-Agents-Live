"""Chat handlers."""

from aiogram import F, Router
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from core_client import CoreClient, CoreClientError
from formatters import markdown_to_telegram_html
from session_store import get_session_store

router = Router()
core_client = CoreClient()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    if message.chat is None:
        return
    await message.answer(
        "Привет! Я <b>Айра</b> — консультант llmstart.ru.\n"
        "Задайте вопрос о курсах или напишите, если готовы записаться.",
        parse_mode=ParseMode.HTML,
    )


@router.message(F.text)
async def handle_text(message: Message) -> None:
    if message.chat is None or message.bot is None or not message.text:
        return

    session_id = get_session_store().get_session_id(message.chat.id)
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    try:
        response = await core_client.send_message(session_id, message.text)
        html_reply = markdown_to_telegram_html(response.reply)
        await message.answer(html_reply or response.reply, parse_mode=ParseMode.HTML)
    except CoreClientError as exc:
        await message.answer(exc.user_message)
