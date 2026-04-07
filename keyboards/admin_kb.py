from datetime import datetime, timedelta
from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import MASSAGE_TIME_SLOTS, WAX_TIME_SLOTS, BOOKING_DAYS_AHEAD

_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


class AdminCancelCallback(CallbackData, prefix="adm_cancel"):
    booking_id: int


class AdminMenuCallback(CallbackData, prefix="adm_menu"):
    action: str  # "slot" | "day" | "unblock" | "list"


class AdminBlockDateCallback(CallbackData, prefix="adm_bd"):
    date: str   # ДД.ММ.ГГГГ
    mode: str   # "slot" | "day"


class AdminBlockTimeCallback(CallbackData, prefix="adm_bt"):
    date: str
    time: str   # ЧЧ_ММ


class AdminUnblockCallback(CallbackData, prefix="adm_ub"):
    block_id: int


class AdminViewDateCallback(CallbackData, prefix="adm_vd"):
    date: str


def get_admin_cancel_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="❌ Отменить запись",
            callback_data=AdminCancelCallback(booking_id=booking_id).pack(),
        ),
    ]])


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔒 Закрыть слот",  callback_data=AdminMenuCallback(action="slot").pack()),
            InlineKeyboardButton(text="📅 Закрыть день",  callback_data=AdminMenuCallback(action="day").pack()),
        ],
        [
            InlineKeyboardButton(text="🔓 Разблокировать", callback_data=AdminMenuCallback(action="unblock").pack()),
            InlineKeyboardButton(text="📋 Блокировки",     callback_data=AdminMenuCallback(action="list").pack()),
        ],
    ])


def get_admin_date_keyboard(mode: str) -> InlineKeyboardMarkup:
    today = datetime.now().date()
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []

    for offset in range(1, BOOKING_DAYS_AHEAD + 1):
        date = today + timedelta(days=offset)
        label = f"{_WEEKDAYS[date.weekday()]}, {date.strftime('%d.%m')}"
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=AdminBlockDateCallback(
                date=date.strftime("%d.%m.%Y"), mode=mode
            ).pack(),
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=AdminMenuCallback(action="back").pack())])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_time_keyboard(date: str) -> InlineKeyboardMarkup:
    """Все слоты: сначала массажные, потом восковые."""
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []

    # Объединяем и сортируем все уникальные слоты
    all_slots = sorted(set(MASSAGE_TIME_SLOTS + WAX_TIME_SLOTS))
    for slot in all_slots:
        label = slot
        if slot in MASSAGE_TIME_SLOTS and slot not in WAX_TIME_SLOTS:
            label = f"💆 {slot}"
        elif slot in WAX_TIME_SLOTS and slot not in MASSAGE_TIME_SLOTS:
            label = f"🍯 {slot}"
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=AdminBlockTimeCallback(
                date=date, time=slot.replace(":", "_")
            ).pack(),
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(
        text="◀️ Назад",
        callback_data=AdminBlockDateCallback(date=date, mode="slot_back").pack(),
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_view_dates_keyboard() -> InlineKeyboardMarkup:
    """Выбор даты для просмотра записей (сегодня + 14 дней)."""
    today = datetime.now().date()
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []

    # Сегодня отдельно
    today_label = f"📅 Сегодня, {today.strftime('%d.%m')}"
    buttons.append([InlineKeyboardButton(
        text=today_label,
        callback_data=AdminViewDateCallback(date=today.strftime("%d.%m.%Y")).pack(),
    )])

    for offset in range(1, BOOKING_DAYS_AHEAD + 1):
        date = today + timedelta(days=offset)
        label = f"{_WEEKDAYS[date.weekday()]}, {date.strftime('%d.%m')}"
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=AdminViewDateCallback(date=date.strftime("%d.%m.%Y")).pack(),
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_unblock_keyboard(blocks: list) -> InlineKeyboardMarkup:
    buttons = []
    for b in blocks:
        slot = b["time"] if b["time"] else "весь день"
        reason = f" — {b['reason']}" if b.get("reason") else ""
        buttons.append([InlineKeyboardButton(
            text=f"🔓 {b['date']}  {slot}{reason}",
            callback_data=AdminUnblockCallback(block_id=b["id"]).pack(),
        )])
    buttons.append([InlineKeyboardButton(
        text="◀️ Назад", callback_data=AdminMenuCallback(action="back").pack()
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
