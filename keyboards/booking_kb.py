"""
Клавиатуры для сценария записи.
Время хранится с _ вместо : (ограничение CallbackData).
"""

from datetime import datetime, timedelta
from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import BOOKING_DAYS_AHEAD, SERVICES

_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

_CAT_LABELS = {
    "adjmal":    "💆 Аджмал — массаж",
    "milana":    "💆 Милана — массаж",
    "fourhands": "🤝 Массаж в 4 руки",
    "wax":       "🍯 Депиляция воском  (⚠️ ТОЛЬКО ДЛЯ ЖЕНЩИН)",
}


class BookingCategoryCallback(CallbackData, prefix="bk_cat"):
    category: str


class BookingServiceCallback(CallbackData, prefix="bk_svc"):
    service_id: str


class BookingDateCallback(CallbackData, prefix="bk_date"):
    date: str  # ДД.ММ.ГГГГ


class BookingTimeCallback(CallbackData, prefix="bk_time"):
    time: str  # ЧЧ_ММ


class BookingConfirmCallback(CallbackData, prefix="bk_ok"):
    action: str  # "yes" | "no"


def get_booking_categories_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=label,
            callback_data=BookingCategoryCallback(category=cat).pack(),
        )]
        for cat, label in _CAT_LABELS.items()
    ]
    buttons.append([_cancel_btn()])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_booking_services_keyboard(category: str) -> InlineKeyboardMarkup:
    items = [s for s in SERVICES if s["category"] == category]
    buttons = [
        [InlineKeyboardButton(
            text=f"{s['name']}  —  {s['price']}  ·  {s['duration_min']} мин",
            callback_data=BookingServiceCallback(service_id=s["id"]).pack(),
        )]
        for s in items
    ]
    buttons.append([_cancel_btn()])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_dates_keyboard() -> InlineKeyboardMarkup:
    today = datetime.now().date()
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    added, offset = 0, 1

    while added < BOOKING_DAYS_AHEAD:
        date = today + timedelta(days=offset)
        offset += 1
        label = f"{_WEEKDAYS[date.weekday()]}, {date.strftime('%d.%m')}"
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=BookingDateCallback(date=date.strftime("%d.%m.%Y")).pack(),
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
        added += 1

    if row:
        buttons.append(row)
    buttons.append([_cancel_btn()])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_times_keyboard(available_slots: List[str]) -> InlineKeyboardMarkup:
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []

    for slot in available_slots:
        row.append(InlineKeyboardButton(
            text=slot,
            callback_data=BookingTimeCallback(time=slot.replace(":", "_")).pack(),
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)
    buttons.append([_cancel_btn()])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_skip_comment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ Пропустить", callback_data="bk_skip_comment")],
        [_cancel_btn()],
    ])


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=BookingConfirmCallback(action="yes").pack(),
        ),
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=BookingConfirmCallback(action="no").pack(),
        ),
    ]])


def _cancel_btn() -> InlineKeyboardButton:
    return InlineKeyboardButton(text="✖ Отменить запись", callback_data="bk_cancel")
