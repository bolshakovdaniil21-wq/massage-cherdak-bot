"""
Сценарий записи (FSM):
  категория → услуга → имя → телефон → дата → время → комментарий → подтверждение
"""

import logging
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID, SERVICES_BY_ID, SPECIALISTS
from database import save_booking
from keyboards.admin_kb import get_admin_cancel_keyboard
from keyboards.booking_kb import (
    BookingCategoryCallback,
    BookingConfirmCallback,
    BookingDateCallback,
    BookingServiceCallback,
    BookingTimeCallback,
    get_booking_categories_keyboard,
    get_booking_services_keyboard,
    get_confirm_keyboard,
    get_dates_keyboard,
    get_skip_comment_keyboard,
    get_times_keyboard,
)
from keyboards.main_menu import get_main_menu
from keyboards.services_kb import ServiceCallback
from states.booking import BookingStates
from utils.slots import get_available_slots
from utils.validators import format_phone, validate_name, validate_phone

router = Router()
logger = logging.getLogger(__name__)

_CAT_INFO = {
    "adjmal":    "👤 Мастер: <b>Аджмал</b>",
    "milana":    "👤 Мастер: <b>Милана</b>",
    "fourhands": "👤 Мастера: <b>Аджмал + Милана</b>",
    "wax":       "👤 Мастер: <b>Милана</b>  ⚠️ ТОЛЬКО ДЛЯ ЖЕНЩИН",
}


async def _notify_admin(bot: Bot, data: dict, booking_id: int) -> None:
    comment = data.get("comment") or "—"
    tg = f"@{data['username']}" if data.get("username") else "не указан"
    text = (
        "🔔 <b>Новая запись!</b>\n\n"
        f"👤 <b>Клиент:</b> {data['name']}\n"
        f"📱 <b>Телефон:</b> {data['phone']}\n"
        f"💬 <b>Telegram:</b> {tg}\n\n"
        f"💆 <b>Услуга:</b> {data['service_name']}\n"
        f"👤 <b>Мастер:</b> {data['specialist_name']}\n"
        f"📅 <b>Дата:</b> {data['date']}\n"
        f"🕐 <b>Время:</b> {data['time']}\n"
        f"⏱ <b>Длительность:</b> {data['duration_min']} мин\n\n"
        f"📝 <b>Комментарий:</b> {comment}"
    )
    try:
        await bot.send_message(
            ADMIN_ID, text, parse_mode="HTML",
            reply_markup=get_admin_cancel_keyboard(booking_id),
        )
    except Exception as e:
        logger.error("Не удалось уведомить админа: %s", e)


async def _show_confirmation(msg: Message, state: FSMContext, edit: bool = False) -> None:
    data = await state.get_data()
    comment = data.get("comment") or "—"
    text = (
        "📋 <b>Проверьте вашу запись:</b>\n\n"
        f"💆 <b>Услуга:</b> {data['service_name']}\n"
        f"👤 <b>Мастер:</b> {data['specialist_name']}\n"
        f"👤 <b>Имя:</b> {data['name']}\n"
        f"📱 <b>Телефон:</b> {data['phone']}\n"
        f"📅 <b>Дата:</b> {data['date']}\n"
        f"🕐 <b>Время:</b> {data['time']}\n"
        f"📝 <b>Комментарий:</b> {comment}\n\n"
        "Всё верно?"
    )
    kb = get_confirm_keyboard()
    if edit:
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await msg.answer(text, reply_markup=kb, parse_mode="HTML")
    await state.set_state(BookingStates.confirming)


# ── Вход из главного меню ──────────────────────────────────────

@router.message(F.text == "📅 Записаться")
async def start_booking(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "📅 <b>Запись на сеанс</b>\n\nВыберите категорию:",
        reply_markup=get_booking_categories_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.choosing_category)


# ── Вход из карточки услуги ────────────────────────────────────

@router.callback_query(ServiceCallback.filter(F.action == "book"))
async def start_booking_from_service(
    callback: CallbackQuery, callback_data: ServiceCallback, state: FSMContext
) -> None:
    await state.clear()
    service = SERVICES_BY_ID.get(callback_data.service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    spec = SPECIALISTS[service["specialist_id"]]
    await state.update_data(
        service_id=service["id"],
        service_name=service["name"],
        duration_min=service["duration_min"],
        slot_type=service["slot_type"],
        specialist_id=spec["id"],
        specialist_name=spec["name"],
    )
    await callback.message.answer(
        f"💆 <b>{service['name']}</b>  ·  {service['duration_min']} мин\n"
        f"👤 Мастер: <b>{spec['name']}</b>\n\n"
        "✏️ Введите ваше <b>имя</b>:",
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.entering_name)
    await callback.answer()


# ── Шаг 1: категория ──────────────────────────────────────────

@router.callback_query(BookingCategoryCallback.filter(), BookingStates.choosing_category)
async def process_category(
    callback: CallbackQuery, callback_data: BookingCategoryCallback, state: FSMContext
) -> None:
    cat = callback_data.category
    info = _CAT_INFO.get(cat, "")
    from keyboards.booking_kb import _CAT_LABELS
    label = _CAT_LABELS.get(cat, cat)
    await callback.message.edit_text(
        f"<b>{label}</b>\n\n{info}\n\nВыберите услугу:",
        reply_markup=get_booking_services_keyboard(cat),
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.choosing_service)
    await callback.answer()


# ── Шаг 2: услуга ─────────────────────────────────────────────

@router.callback_query(BookingServiceCallback.filter(), BookingStates.choosing_service)
async def process_service(
    callback: CallbackQuery, callback_data: BookingServiceCallback, state: FSMContext
) -> None:
    service = SERVICES_BY_ID.get(callback_data.service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    spec = SPECIALISTS[service["specialist_id"]]
    await state.update_data(
        service_id=service["id"],
        service_name=service["name"],
        duration_min=service["duration_min"],
        slot_type=service["slot_type"],
        specialist_id=spec["id"],
        specialist_name=spec["name"],
    )
    await callback.message.edit_text(
        f"💆 <b>{service['name']}</b>  ·  {service['duration_min']} мин\n"
        f"👤 Мастер: <b>{spec['name']}</b>\n\n"
        "✏️ Введите ваше <b>имя</b>:",
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.entering_name)
    await callback.answer()


# ── Шаг 3: имя ────────────────────────────────────────────────

@router.message(BookingStates.entering_name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not validate_name(name):
        await message.answer("⚠️ Введите корректное имя (минимум 2 буквы).")
        return
    await state.update_data(name=name)
    await message.answer(
        f"✅ <b>{name}</b>\n\n"
        "📱 Введите ваш <b>номер телефона</b>:\n<i>Пример: +79991234567</i>",
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.entering_phone)


# ── Шаг 4: телефон ────────────────────────────────────────────

@router.message(BookingStates.entering_phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone_raw = message.text.strip()
    if not validate_phone(phone_raw):
        await message.answer(
            "⚠️ Некорректный номер. Введите российский номер.\n"
            "<i>Пример: +79991234567</i>",
            parse_mode="HTML",
        )
        return
    phone = format_phone(phone_raw)
    await state.update_data(phone=phone)
    await message.answer(
        f"✅ Телефон: <b>{phone}</b>\n\n📅 Выберите <b>дату</b>:",
        reply_markup=get_dates_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.choosing_date)


# ── Шаг 5: дата ───────────────────────────────────────────────

@router.callback_query(BookingDateCallback.filter(), BookingStates.choosing_date)
async def process_date(
    callback: CallbackQuery, callback_data: BookingDateCallback, state: FSMContext
) -> None:
    data = await state.get_data()
    date = callback_data.date
    await state.update_data(date=date)

    available = await get_available_slots(
        specialist_id=data["specialist_id"],
        date=date,
        duration_min=data["duration_min"],
        slot_type=data.get("slot_type", "massage"),
    )

    if not available:
        await callback.message.edit_text(
            f"😔 На <b>{date}</b> свободных окон нет.\n\nВыберите другой день:",
            reply_markup=get_dates_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"✅ Дата: <b>{date}</b>\n\n🕐 Выберите <b>время</b>:",
        reply_markup=get_times_keyboard(available),
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.choosing_time)
    await callback.answer()


# ── Шаг 6: время ──────────────────────────────────────────────

@router.callback_query(BookingTimeCallback.filter(), BookingStates.choosing_time)
async def process_time(
    callback: CallbackQuery, callback_data: BookingTimeCallback, state: FSMContext
) -> None:
    time_value = callback_data.time.replace("_", ":")
    await state.update_data(time=time_value)
    await callback.message.edit_text(
        f"✅ Время: <b>{time_value}</b>\n\n"
        "📝 Есть пожелания? Напишите или нажмите <b>«Пропустить»</b>:",
        reply_markup=get_skip_comment_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(BookingStates.entering_comment)
    await callback.answer()


# ── Шаг 7: комментарий ────────────────────────────────────────

@router.message(BookingStates.entering_comment)
async def process_comment(message: Message, state: FSMContext) -> None:
    await state.update_data(comment=message.text.strip())
    await _show_confirmation(message, state)


@router.callback_query(F.data == "bk_skip_comment", BookingStates.entering_comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(comment=None)
    await _show_confirmation(callback.message, state, edit=True)
    await callback.answer()


# ── Шаг 8: подтверждение ──────────────────────────────────────

@router.callback_query(BookingConfirmCallback.filter(F.action == "yes"), BookingStates.confirming)
async def confirm_booking(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    user = callback.from_user

    booking_id = await save_booking(
        user_id=user.id,
        username=user.username,
        name=data["name"],
        phone=data["phone"],
        service_id=data["service_id"],
        service_name=data["service_name"],
        specialist_id=data["specialist_id"],
        specialist_name=data["specialist_name"],
        duration_min=data["duration_min"],
        slot_type=data.get("slot_type", "massage"),
        date=data["date"],
        time=data["time"],
        comment=data.get("comment"),
    )

    await _notify_admin(bot, {**data, "username": user.username}, booking_id)
    await state.clear()

    await callback.message.edit_text(
        "✅ <b>Запись принята!</b>\n\n"
        f"💆 <b>Услуга:</b> {data['service_name']}\n"
        f"👤 <b>Мастер:</b> {data['specialist_name']}\n"
        f"📅 <b>Дата:</b> {data['date']}\n"
        f"🕐 <b>Время:</b> {data['time']}\n\n"
        "Мы свяжемся с вами для подтверждения. До встречи! 💙\n\n"
        "<i>Отменить запись можно через «🗓 Мои записи»</i>",
        parse_mode="HTML",
    )
    await callback.answer("Запись оформлена! ✅")


@router.callback_query(BookingConfirmCallback.filter(F.action == "no"), BookingStates.confirming)
async def cancel_at_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "❌ Запись отменена.\nДля новой записи нажмите «📅 Записаться»."
    )
    await callback.answer()


@router.callback_query(F.data == "bk_cancel")
async def cancel_any_step(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "❌ Запись отменена.\nДля новой записи нажмите «📅 Записаться»."
    )
    await callback.answer()
