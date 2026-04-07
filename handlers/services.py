from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import SERVICES_BY_ID, SPECIALISTS
from keyboards.services_kb import (
    ServiceCallback,
    _CAT_LABELS,
    get_categories_keyboard,
    get_service_detail_keyboard,
    get_services_by_category,
)

router = Router()

_CAT_INFO = {
    "adjmal":    "👤 Мастер: <b>Аджмал</b>",
    "milana":    "👤 Мастер: <b>Милана</b>",
    "fourhands": "👤 Мастера: <b>Аджмал + Милана</b> (работают одновременно)",
    "wax":       "👤 Мастер: <b>Милана</b> — депиляция воском\n⚠️ <b>УСЛУГИ ТОЛЬКО ДЛЯ ЖЕНЩИН</b>",
}


@router.message(F.text == "💆 Услуги")
async def show_categories(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "💆 <b>Наши услуги</b>\n\nВыберите категорию:",
        reply_markup=get_categories_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(ServiceCallback.filter(F.action == "list"))
async def back_to_categories(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "💆 <b>Наши услуги</b>\n\nВыберите категорию:",
        reply_markup=get_categories_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(ServiceCallback.filter(F.action.startswith("cat_")))
async def show_category(callback: CallbackQuery, callback_data: ServiceCallback) -> None:
    category = callback_data.action.replace("cat_", "")
    label = _CAT_LABELS.get(category, "Услуги")
    info  = _CAT_INFO.get(category, "")
    header = f"<b>{label}</b>\n\n{info}\n\nВыберите услугу:"

    await callback.message.edit_text(
        header,
        reply_markup=get_services_by_category(category),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(ServiceCallback.filter(F.action == "view"))
async def show_service_detail(callback: CallbackQuery, callback_data: ServiceCallback) -> None:
    service = SERVICES_BY_ID.get(callback_data.service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    spec = SPECIALISTS.get(service["specialist_id"], {})
    spec_name = spec.get("name", "—")

    text = (
        f"<b>{service['name']}</b>\n\n"
        f"📝 {service['description']}\n\n"
        f"⏱ <b>Длительность:</b> {service['duration_min']} мин\n"
        f"💰 <b>Стоимость:</b> {service['price']}\n"
        f"👤 <b>Мастер:</b> {spec_name}"
    )
    if service.get("women_only"):
        text += "\n\n⚠️ <b>ТОЛЬКО ДЛЯ ЖЕНЩИН</b>"

    await callback.message.edit_text(
        text,
        reply_markup=get_service_detail_keyboard(service["id"]),
        parse_mode="HTML",
    )
    await callback.answer()
