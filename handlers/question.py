from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMIN_ID
from states.question import QuestionStates

import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "❓ Задать вопрос")
async def ask_question_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❓ <b>Задать вопрос</b>\n\n"
        "Напишите ваш вопрос — мы передадим его администратору:",
        parse_mode="HTML",
    )
    await state.set_state(QuestionStates.entering_question)


@router.message(QuestionStates.entering_question)
async def process_question(message: Message, state: FSMContext, bot: Bot) -> None:
    question = message.text.strip()
    user = message.from_user
    tg = f"@{user.username}" if user.username else "не указан"
    name = user.full_name or "Неизвестно"

    admin_text = (
        "❓ <b>Вопрос от клиента</b>\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"💬 <b>Telegram:</b> {tg}\n\n"
        f"📝 <b>Вопрос:</b>\n{question}"
    )
    try:
        await bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")
    except Exception as e:
        logger.error("Не удалось отправить вопрос администратору: %s", e)

    await state.clear()
    await message.answer(
        "✅ Ваш вопрос отправлен!\n\nАдминистратор свяжется с вами в ближайшее время."
    )
