from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import SERVICES


class ServiceCallback(CallbackData, prefix="svc"):
    service_id: str
    action: str  # "view" | "list" | "book" | "cat_*"


_CAT_LABELS = {
    "adjmal":    "💆 Аджмал — массаж",
    "milana":    "💆 Милана — массаж",
    "fourhands": "🤝 Массаж в 4 руки",
    "wax":       "🍯 Депиляция воском",
}


def get_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=label,
            callback_data=ServiceCallback(service_id="", action=f"cat_{cat}").pack(),
        )]
        for cat, label in _CAT_LABELS.items()
    ])


def get_services_by_category(category: str) -> InlineKeyboardMarkup:
    items = [s for s in SERVICES if s["category"] == category]
    buttons = [
        [InlineKeyboardButton(
            text=f"{s['name']}  —  {s['price']}  ·  {s['duration_min']} мин",
            callback_data=ServiceCallback(service_id=s["id"], action="view").pack(),
        )]
        for s in items
    ]
    buttons.append([InlineKeyboardButton(
        text="◀️ К категориям",
        callback_data=ServiceCallback(service_id="", action="list").pack(),
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_service_detail_keyboard(service_id: str) -> InlineKeyboardMarkup:
    from config import SERVICES_BY_ID
    s = SERVICES_BY_ID.get(service_id, {})
    cat = s.get("category", "adjmal")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📅 Записаться на эту услугу",
            callback_data=ServiceCallback(service_id=service_id, action="book").pack(),
        )],
        [InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=ServiceCallback(service_id="", action=f"cat_{cat}").pack(),
        )],
    ])
