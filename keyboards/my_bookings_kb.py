from typing import List, Dict

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class CancelBookingCallback(CallbackData, prefix="cbk"):
    booking_id: int
    action: str  # "ask" | "yes" | "no"


def get_my_bookings_keyboard(bookings: List[Dict]) -> InlineKeyboardMarkup:
    buttons = []
    for b in bookings:
        label = f"❌  {b['date']} {b['time']} — {b['service_name'][:25]}"
        buttons.append([InlineKeyboardButton(
            text=label,
            callback_data=CancelBookingCallback(booking_id=b["id"], action="ask").pack(),
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_confirm_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Да, отменить",
            callback_data=CancelBookingCallback(booking_id=booking_id, action="yes").pack(),
        ),
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=CancelBookingCallback(booking_id=booking_id, action="no").pack(),
        ),
    ]])
