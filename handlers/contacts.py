from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import (
    ADDRESS, MAP_URL, PHONE, SPECIALISTS,
    STUDIO_NAME, TELEGRAM_CONTACT, WORK_HOURS,
)

router = Router()


@router.message(F.text == "📍 Адрес и информация")
async def show_contacts(message: Message, state: FSMContext) -> None:
    await state.clear()

    masters_text = "\n".join(
        f"  • <b>{s['name']}</b> — {s['note']}"
        for s in SPECIALISTS.values()
    )

    text = (
        f"📍 <b>{STUDIO_NAME}</b>\n\n"
        f"🏠 <b>Адрес:</b>\n{ADDRESS}\n\n"
        f"📞 <b>Телефон:</b>\n{PHONE}\n\n"
        f"💬 <b>Telegram:</b>\n{TELEGRAM_CONTACT}\n\n"
        f"🕐 <b>Часы работы:</b>\n{WORK_HOURS}\n\n"
        f"👤 <b>Наши мастера:</b>\n{masters_text}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗺 Открыть на карте", url=MAP_URL)],
        [InlineKeyboardButton(
            text="💬 Написать в Telegram",
            url=f"https://t.me/{TELEGRAM_CONTACT.lstrip('@')}",
        )],
    ])
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
