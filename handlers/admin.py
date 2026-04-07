"""
Команды администратора:
  /admin    — меню управления (кнопки для закрытия слотов/дней)
  /bookings — записи на сегодня
  /blocks   — список блокировок
"""

import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from keyboards.main_menu import get_admin_menu

from config import ADMIN_ID, MASSAGE_TIME_SLOTS, WAX_TIME_SLOTS
from database import (
    block_slot, delete_booking, get_all_blocked,
    get_booking_by_id, get_bookings, unblock_by_id,
)
from keyboards.admin_kb import (
    AdminBlockDateCallback,
    AdminBlockTimeCallback,
    AdminCancelCallback,
    AdminMenuCallback,
    AdminUnblockCallback,
    AdminViewDateCallback,
    get_admin_cancel_keyboard,
    get_admin_date_keyboard,
    get_admin_menu_keyboard,
    get_admin_time_keyboard,
    get_admin_unblock_keyboard,
    get_admin_view_dates_keyboard,
)

router = Router()
logger = logging.getLogger(__name__)


def _is_admin(uid: int) -> bool:
    return uid == ADMIN_ID


# ── /admin + кнопки ───────────────────────────────────────────

async def _send_admin_panel(message: Message) -> None:
    await message.answer(
        "⚙️ <b>Управление расписанием</b>\n\nВыберите действие:",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    await _send_admin_panel(message)


@router.message(F.text == "🔒 Закрыть слот")
async def btn_close_slot(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    await message.answer(
        "🔒 <b>Закрыть слот</b>\n\nВыберите дату:",
        reply_markup=get_admin_date_keyboard("slot"),
        parse_mode="HTML",
    )


@router.message(F.text == "📅 Закрыть день/дни")
async def btn_close_day(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    await message.answer(
        "📅 <b>Закрыть день</b>\n\nВыберите дату:",
        reply_markup=get_admin_date_keyboard("day"),
        parse_mode="HTML",
    )


@router.message(F.text == "🔓 Разблокировать")
async def btn_unblock(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    blocks = await get_all_blocked()
    if not blocks:
        await message.answer("✅ Нет активных блокировок.", reply_markup=get_admin_menu())
    else:
        await message.answer(
            "🔓 <b>Нажмите на блокировку чтобы снять её:</b>",
            reply_markup=get_admin_unblock_keyboard(blocks),
            parse_mode="HTML",
        )


@router.message(F.text == "📋 Все блокировки")
async def btn_list_blocks(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    blocks = await get_all_blocked()
    if not blocks:
        await message.answer("✅ Нет активных блокировок.", reply_markup=get_admin_menu())
        return
    lines = ["🔒 <b>Активные блокировки:</b>\n"]
    for b in blocks:
        slot = b["time"] if b["time"] else "весь день"
        reason = f" — {b['reason']}" if b.get("reason") else ""
        lines.append(f"📅 <b>{b['date']}</b>  🕐 {slot}{reason}")
    lines.append("\n<i>Для снятия: нажмите «🔓 Разблокировать»</i>")
    await message.answer("\n".join(lines), parse_mode="HTML", reply_markup=get_admin_menu())


@router.callback_query(AdminMenuCallback.filter(F.action == "back"))
async def admin_back_to_menu(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "⚙️ <b>Управление расписанием</b>\n\nВыберите действие:",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ── Закрыть слот ──────────────────────────────────────────────

@router.callback_query(AdminMenuCallback.filter(F.action == "slot"))
async def admin_choose_date_for_slot(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "🔒 <b>Закрыть слот</b>\n\nВыберите дату:",
        reply_markup=get_admin_date_keyboard("slot"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(AdminBlockDateCallback.filter(F.mode == "slot"))
async def admin_choose_time_for_slot(
    callback: CallbackQuery, callback_data: AdminBlockDateCallback
) -> None:
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        f"🔒 Дата: <b>{callback_data.date}</b>\n\nВыберите время для закрытия:",
        reply_markup=get_admin_time_keyboard(callback_data.date),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(AdminBlockTimeCallback.filter())
async def admin_block_time(
    callback: CallbackQuery, callback_data: AdminBlockTimeCallback
) -> None:
    if not _is_admin(callback.from_user.id):
        return
    time = callback_data.time.replace("_", ":")
    await block_slot(callback_data.date, time, reason=None)
    await callback.message.edit_text(
        f"✅ Слот <b>{callback_data.date} {time}</b> закрыт.\n\n"
        "Клиенты не смогут записаться на это время.",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer("Слот закрыт.")


# ── Закрыть день ──────────────────────────────────────────────

@router.callback_query(AdminMenuCallback.filter(F.action == "day"))
async def admin_choose_date_for_day(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "📅 <b>Закрыть день</b>\n\nВыберите дату:",
        reply_markup=get_admin_date_keyboard("day"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(AdminBlockDateCallback.filter(F.mode == "day"))
async def admin_block_day(
    callback: CallbackQuery, callback_data: AdminBlockDateCallback
) -> None:
    if not _is_admin(callback.from_user.id):
        return
    await block_slot(callback_data.date, time=None, reason="выходной")
    await callback.message.edit_text(
        f"✅ День <b>{callback_data.date}</b> полностью закрыт.\n\n"
        "Запись на этот день недоступна для клиентов.",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer("День закрыт.")


# ── Разблокировать ────────────────────────────────────────────

@router.callback_query(AdminMenuCallback.filter(F.action == "unblock"))
async def admin_show_unblock(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        return
    blocks = await get_all_blocked()
    if not blocks:
        await callback.message.edit_text(
            "✅ Нет активных блокировок.",
            reply_markup=get_admin_menu_keyboard(),
        )
    else:
        await callback.message.edit_text(
            "🔓 <b>Нажмите на блокировку чтобы снять её:</b>",
            reply_markup=get_admin_unblock_keyboard(blocks),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(AdminUnblockCallback.filter())
async def admin_unblock(
    callback: CallbackQuery, callback_data: AdminUnblockCallback
) -> None:
    if not _is_admin(callback.from_user.id):
        return
    deleted = await unblock_by_id(callback_data.block_id)
    if deleted:
        await callback.answer("✅ Блокировка снята.")
    else:
        await callback.answer("Блокировка уже была снята.", show_alert=True)

    blocks = await get_all_blocked()
    if not blocks:
        await callback.message.edit_text(
            "✅ Все блокировки сняты.",
            reply_markup=get_admin_menu_keyboard(),
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=get_admin_unblock_keyboard(blocks)
        )


# ── Список блокировок ─────────────────────────────────────────

@router.callback_query(AdminMenuCallback.filter(F.action == "list"))
async def admin_list_blocks(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        return
    blocks = await get_all_blocked()
    if not blocks:
        await callback.message.edit_text(
            "✅ Нет активных блокировок.",
            reply_markup=get_admin_menu_keyboard(),
        )
    else:
        lines = ["🔒 <b>Активные блокировки:</b>\n"]
        for b in blocks:
            slot = b["time"] if b["time"] else "весь день"
            reason = f" — {b['reason']}" if b.get("reason") else ""
            lines.append(f"📅 <b>{b['date']}</b>  🕐 {slot}{reason}")
        lines.append("\n<i>Для снятия: нажмите «🔓 Разблокировать»</i>")
        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="HTML",
        )
    await callback.answer()


# ── Все записи (кнопка) ───────────────────────────────────────

@router.message(F.text == "📒 Все записи")
async def btn_all_bookings(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    await message.answer(
        "📒 <b>Все записи</b>\n\nВыберите дату:",
        reply_markup=get_admin_view_dates_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(AdminViewDateCallback.filter())
async def admin_view_bookings_for_date(
    callback: CallbackQuery, callback_data: AdminViewDateCallback
) -> None:
    if not _is_admin(callback.from_user.id):
        return

    date = callback_data.date
    bookings = await get_bookings(date=date)

    if not bookings:
        await callback.message.edit_text(
            f"📅 На <b>{date}</b> записей нет.",
            parse_mode="HTML",
        )
        await callback.answer()
        return

    lines = [f"📒 <b>Записи на {date}</b>  ({len(bookings)} шт.)\n"]
    for b in bookings:
        comment = b.get("comment") or "—"
        tg = f"@{b['username']}" if b.get("username") else "нет"
        lines.append(
            f"🕐 <b>{b['time']}</b>  —  {b['service_name']}\n"
            f"   👤 {b['name']}  📱 {b['phone']}  💬 {tg}\n"
            f"   Мастер: {b['specialist_name']}  ⏱ {b['duration_min']} мин\n"
            f"   📝 {comment}\n"
        )

    # Разбиваем на части если сообщение длинное
    text = "\n".join(lines)
    if len(text) > 4000:
        await callback.message.edit_text(
            f"📒 <b>Записи на {date}</b>  ({len(bookings)} шт.)",
            parse_mode="HTML",
        )
        for b in bookings:
            comment = b.get("comment") or "—"
            tg = f"@{b['username']}" if b.get("username") else "нет"
            await callback.message.answer(
                f"🕐 <b>{b['time']}</b>  —  {b['service_name']}\n"
                f"👤 {b['name']}  📱 {b['phone']}  💬 {tg}\n"
                f"Мастер: {b['specialist_name']}  ⏱ {b['duration_min']} мин\n"
                f"📝 {comment}",
                parse_mode="HTML",
                reply_markup=get_admin_cancel_keyboard(b["id"]),
            )
    else:
        await callback.message.edit_text(text, parse_mode="HTML")
        # Кнопки отмены отдельно для каждой записи
        for b in bookings:
            comment = b.get("comment") or "—"
            tg = f"@{b['username']}" if b.get("username") else "нет"
            await callback.message.answer(
                f"🕐 <b>{b['time']}</b>  —  {b['service_name']}\n"
                f"👤 {b['name']}  📱 {b['phone']}  💬 {tg}\n"
                f"Мастер: {b['specialist_name']}  ⏱ {b['duration_min']} мин\n"
                f"📝 {comment}",
                parse_mode="HTML",
                reply_markup=get_admin_cancel_keyboard(b["id"]),
            )

    await callback.answer()


# ── /bookings ─────────────────────────────────────────────────

@router.message(Command("bookings"))
async def cmd_bookings(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    today = datetime.now().strftime("%d.%m.%Y")
    bookings = await get_bookings(date=today)
    if not bookings:
        await message.answer(f"📅 На <b>{today}</b> записей нет.", parse_mode="HTML")
        return
    for b in bookings:
        comment = b.get("comment") or "—"
        await message.answer(
            f"🕐 <b>{b['time']}</b>  —  {b['service_name']}\n"
            f"👤 {b['name']}  📱 {b['phone']}\n"
            f"Мастер: {b['specialist_name']}  ⏱ {b['duration_min']} мин\n"
            f"📝 {comment}",
            parse_mode="HTML",
            reply_markup=get_admin_cancel_keyboard(b["id"]),
        )


# ── /blocks ───────────────────────────────────────────────────

@router.message(Command("blocks"))
async def cmd_blocks(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return
    blocks = await get_all_blocked()
    if not blocks:
        await message.answer("✅ Нет активных блокировок.")
        return
    lines = ["🔒 <b>Активные блокировки:</b>\n"]
    for b in blocks:
        slot = b["time"] if b["time"] else "весь день"
        lines.append(f"📅 <b>{b['date']}</b>  🕐 {slot}")
    await message.answer("\n".join(lines), parse_mode="HTML")


# ── Отмена записи по кнопке ───────────────────────────────────

@router.callback_query(AdminCancelCallback.filter())
async def admin_cancel_booking(
    callback: CallbackQuery, callback_data: AdminCancelCallback, bot: Bot
) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    booking = await get_booking_by_id(callback_data.booking_id)
    if not booking:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("Запись уже отменена.", show_alert=True)
        return

    deleted = await delete_booking(callback_data.booking_id)
    if not deleted:
        await callback.answer("Не удалось отменить.", show_alert=True)
        return

    try:
        await bot.send_message(
            booking["user_id"],
            f"❌ <b>Ваша запись отменена администратором.</b>\n\n"
            f"📅 {booking['date']} в {booking['time']}\n"
            f"💆 {booking['service_name']}\n\n"
            "Если это ошибка — свяжитесь с нами через «❓ Задать вопрос».",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning("Не удалось уведомить клиента: %s", e)

    await callback.message.edit_text(
        f"✅ <b>Запись отменена</b>\n\n"
        f"📅 {booking['date']} {booking['time']}  —  {booking['service_name']}\n"
        f"👤 {booking['name']}  📱 {booking['phone']}\n\n"
        "Окно освобождено.",
        parse_mode="HTML",
    )
    await callback.answer("Запись отменена.")
