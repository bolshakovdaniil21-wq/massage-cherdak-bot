from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💆 Услуги"),      KeyboardButton(text="📅 Записаться")],
            [KeyboardButton(text="🗓 Мои записи"),   KeyboardButton(text="📍 Адрес и информация")],
            [KeyboardButton(text="❓ Задать вопрос"), KeyboardButton(text="🏠 Старт")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел...",
    )


def get_admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💆 Услуги"),        KeyboardButton(text="📅 Записаться")],
            [KeyboardButton(text="🗓 Мои записи"),     KeyboardButton(text="📍 Адрес и информация")],
            [KeyboardButton(text="❓ Задать вопрос"),  KeyboardButton(text="🏠 Старт")],
            [KeyboardButton(text="🔒 Закрыть слот"),   KeyboardButton(text="📅 Закрыть день/дни")],
            [KeyboardButton(text="🔓 Разблокировать"), KeyboardButton(text="📋 Все блокировки")],
            [KeyboardButton(text="📒 Все записи")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел...",
    )
