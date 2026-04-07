"""
Точка входа — фитнес-студия «Чердак»
"""

import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import ADMIN_ID, BOT_TOKEN
from database import get_bookings, init_db
from handlers import admin, booking, contacts, my_bookings, question, services, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def send_daily_summary(bot: Bot) -> None:
    """Отправляет администратору список записей на сегодня."""
    today = datetime.now().strftime("%d.%m.%Y")
    bookings = await get_bookings(date=today)

    if not bookings:
        text = f"📅 <b>Расписание на {today}</b>\n\nЗаписей нет."
    else:
        lines = [f"📅 <b>Расписание на {today}</b>  ({len(bookings)} записей)\n"]
        for b in bookings:
            comment = b.get("comment") or "—"
            tg = f"@{b['username']}" if b.get("username") else "не указан"
            lines.append(
                f"🕐 <b>{b['time']}</b>  ·  {b['service_name']}  ·  {b['duration_min']} мин\n"
                f"   👤 {b['name']}  📱 {b['phone']}  💬 {tg}\n"
                f"   Мастер: {b['specialist_name']}\n"
                f"   📝 {comment}\n"
            )
        text = "\n".join(lines)

    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
        logger.info("Ежедневная сводка отправлена")
    except Exception as e:
        logger.error("Не удалось отправить сводку: %s", e)


async def midnight_scheduler(bot: Bot) -> None:
    """Ждёт полуночи и отправляет сводку, затем повторяет каждые 24 часа."""
    while True:
        now = datetime.now()
        next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        seconds_until_midnight = (next_midnight - now).total_seconds()
        logger.info("Следующая сводка через %.0f сек (в 00:00)", seconds_until_midnight)
        await asyncio.sleep(seconds_until_midnight)
        await send_daily_summary(bot)


async def main() -> None:
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(my_bookings.router)
    dp.include_router(services.router)
    dp.include_router(booking.router)
    dp.include_router(contacts.router)
    dp.include_router(question.router)

    # Запускаем планировщик в фоне
    asyncio.create_task(midnight_scheduler(bot))

    logger.info("Бот запущен. Чердак — поехали!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
