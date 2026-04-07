"""
Просмотр и отмена своих записей клиентом.
"""

import logging
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_ID
from database import delete_booking, get_booking_by_id, get_user_bookings
from keyboards.my_bookings_kb import (
    CancelBookingCallback,
    get_cancel_confirm_keyboard,
    get_my_bookings_keyboard,
)

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "🗓 Мои записи")
async def show_my_bookings(message: Message, state: FSMContext) -> None:
    await state.clear()
    bookings = await get_user_bookings(message.from_user.id)

    if not bookings:
        await message.answer(
            "📭 У вас нет предстоящих записей.\n\n"
            "Записаться можно через «📅 Записаться»."
        )
        return

    lines = ["🗓 <b>Ваши предстоящие записи:</b>\n"]
    for b in bookings:
        lines.append(
            f"📅 <b>{b['date']}</b> в <b>{b['time']}</b>\n"
            f"   💆 {b['service_name']}\n"
            f"   👤 Мастер: {b['specialist_name']}\n"
        )

    lines.append("\nНажмите на запись ниже, чтобы отменить её:")
    await message.answer(
        "\n".join(lines),
        reply_markup=get_my_bookings_keyboard(bookings),
        parse_mode="HTML",
    )


@router.callback_query(CancelBookingCallback.filter(F.action == "ask"))
async def ask_cancel_booking(
    callback: CallbackQuery, callback_data: CancelBookingCallback
) -> None:
    booking = await get_booking_by_id(callback_data.booking_id)
    if not booking:
        await callback.answer("Запись не найдена.", show_alert=True)
        return

    # Проверяем, что запись принадлежит этому пользователю
    if booking["user_id"] != callback.from_user.id:
        await callback.answer("Это не ваша запись.", show_alert=True)
        return

    await callback.message.edit_text(
        f"❓ Отменить запись?\n\n"
        f"📅 <b>{booking['date']}</b> в <b>{booking['time']}</b>\n"
        f"💆 {booking['service_name']}\n"
        f"👤 Мастер: {booking['specialist_name']}",
        reply_markup=get_cancel_confirm_keyboard(callback_data.booking_id),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(CancelBookingCallback.filter(F.action == "yes"))
async def confirm_cancel_booking(
    callback: CallbackQuery, callback_data: CancelBookingCallback, bot: Bot
) -> None:
    booking = await get_booking_by_id(callback_data.booking_id)
    if not booking:
        await callback.answer("Запись не найдена.", show_alert=True)
        return

    if booking["user_id"] != callback.from_user.id:
        await callback.answer("Это не ваша запись.", show_alert=True)
        return

    deleted = await delete_booking(callback_data.booking_id)
    if not deleted:
        await callback.answer("Не удалось отменить. Попробуйте ещё раз.", show_alert=True)
        return

    # Уведомить администратора
    tg = f"@{callback.from_user.username}" if callback.from_user.username else "не указан"
    try:
        await bot.send_message(
            ADMIN_ID,
            f"🔴 <b>Клиент отменил запись</b>\n\n"
            f"💬 Telegram: {tg}\n"
            f"📅 <b>{booking['date']}</b> в <b>{booking['time']}</b>\n"
            f"💆 {booking['service_name']}\n"
            f"👤 Мастер: {booking['specialist_name']}\n"
            f"⏱ {booking['duration_min']} мин\n\n"
            f"Окно освобождено.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error("Не удалось уведомить админа об отмене: %s", e)

    await callback.message.edit_text(
        f"✅ Запись отменена.\n\n"
        f"📅 {booking['date']} в {booking['time']} — {booking['service_name']}\n\n"
        "Окно освобождено. Ждём вас снова! 💙"
    )
    await callback.answer("Запись отменена.")


@router.callback_query(CancelBookingCallback.filter(F.action == "no"))
async def back_to_bookings(
    callback: CallbackQuery, callback_data: CancelBookingCallback
) -> None:
    bookings = await get_user_bookings(callback.from_user.id)
    if not bookings:
        await callback.message.edit_text("📭 Нет предстоящих записей.")
        await callback.answer()
        return

    lines = ["🗓 <b>Ваши предстоящие записи:</b>\n"]
    for b in bookings:
        lines.append(
            f"📅 <b>{b['date']}</b> в <b>{b['time']}</b>\n"
            f"   💆 {b['service_name']}\n"
            f"   👤 Мастер: {b['specialist_name']}\n"
        )
    lines.append("\nНажмите на запись ниже, чтобы отменить её:")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=get_my_bookings_keyboard(bookings),
        parse_mode="HTML",
    )
    await callback.answer()
