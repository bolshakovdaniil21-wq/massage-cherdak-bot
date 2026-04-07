from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMIN_ID, STUDIO_NAME
from keyboards.main_menu import get_admin_menu, get_main_menu

router = Router()


async def _send_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    name = message.from_user.first_name or "Гость"
    is_admin = message.from_user.id == ADMIN_ID

    if is_admin:
        text = (
            f"👋 Здравствуйте, <b>{name}</b>!\n\n"
            f"⚙️ <b>Режим администратора</b>\n\n"
            "Управление расписанием:\n"
            "🔒 Закрыть слот — закрыть конкретное время\n"
            "📅 Закрыть день/дни — закрыть целый день\n"
            "🔓 Разблокировать — снять блокировку\n"
            "📋 Все блокировки — список закрытых окон\n\n"
            "Выберите раздел 👇"
        )
        kb = get_admin_menu()
    else:
        text = (
            f"👋 Здравствуйте, <b>{name}</b>!\n\n"
            f"Добро пожаловать в бот <b>{STUDIO_NAME}</b>.\n\n"
            "Здесь вы можете:\n"
            "💆 Посмотреть услуги мастеров\n"
            "📅 Записаться на удобное время\n"
            "🗓 Посмотреть и отменить свои записи\n"
            "📍 Адрес и информация о студии\n\n"
            "Выберите раздел 👇"
        )
        kb = get_main_menu()

    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await _send_start(message, state)


@router.message(F.text == "🏠 Старт")
async def btn_start(message: Message, state: FSMContext) -> None:
    await _send_start(message, state)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state():
        await state.clear()
        await message.answer("❌ Действие отменено.", reply_markup=get_main_menu())
    else:
        await message.answer("Вы уже в главном меню.", reply_markup=get_main_menu())
