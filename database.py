"""
База данных SQLite для бота «Территория массажа».
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict

import aiosqlite

DB_PATH = "massage_cherdak.db"
logger = logging.getLogger(__name__)


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                username         TEXT,
                name             TEXT    NOT NULL,
                phone            TEXT    NOT NULL,
                service_id       TEXT    NOT NULL,
                service_name     TEXT    NOT NULL,
                specialist_id    TEXT    NOT NULL,
                specialist_name  TEXT    NOT NULL,
                duration_min     INTEGER NOT NULL DEFAULT 60,
                slot_type        TEXT    NOT NULL DEFAULT 'massage',
                date             TEXT    NOT NULL,
                time             TEXT    NOT NULL,
                comment          TEXT,
                created_at       TEXT    NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS blocked_slots (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                date    TEXT NOT NULL,
                time    TEXT,
                reason  TEXT
            )
        """)
        await db.commit()

        # Добавить slot_type если БД старая (без столбца)
        try:
            await db.execute("ALTER TABLE bookings ADD COLUMN slot_type TEXT NOT NULL DEFAULT 'massage'")
            await db.commit()
        except Exception:
            pass

    logger.info("БД инициализирована (%s)", DB_PATH)


# ── Записи клиентов ───────────────────────────────────────────

async def save_booking(
    user_id: int,
    username: Optional[str],
    name: str,
    phone: str,
    service_id: str,
    service_name: str,
    specialist_id: str,
    specialist_name: str,
    duration_min: int,
    slot_type: str,
    date: str,
    time: str,
    comment: Optional[str],
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO bookings
                (user_id, username, name, phone,
                 service_id, service_name,
                 specialist_id, specialist_name, duration_min, slot_type,
                 date, time, comment, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                user_id, username, name, phone,
                service_id, service_name,
                specialist_id, specialist_name, duration_min, slot_type,
                date, time, comment,
                datetime.now().strftime("%d.%m.%Y %H:%M"),
            ),
        )
        await db.commit()
        bid = cursor.lastrowid
        logger.info("Запись #%d: %s %s %s %s", bid, name, service_name, date, time)
        return bid


async def get_bookings_for_specialist(specialist_id: str, date: str) -> List[Dict]:
    """
    Возвращает все записи специалиста на дату.
    Если specialist_id='both' (4 руки), возвращает все записи дня.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if specialist_id == "both":
            cursor = await db.execute(
                "SELECT time, duration_min, slot_type FROM bookings WHERE date=?",
                (date,),
            )
        else:
            cursor = await db.execute(
                """SELECT time, duration_min, slot_type FROM bookings
                   WHERE (specialist_id=? OR specialist_id='both') AND date=?""",
                (specialist_id, date),
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_all_bookings_for_date(date: str) -> List[Dict]:
    """Все записи на дату по всем специалистам (один кабинет)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT time, duration_min, slot_type FROM bookings WHERE date=?",
            (date,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_booking_by_id(booking_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM bookings WHERE id=?", (booking_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_bookings(user_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM bookings WHERE user_id=? ORDER BY date ASC, time ASC",
            (user_id,),
        )
        rows = await cursor.fetchall()
    today = datetime.now().date()
    result = []
    for r in rows:
        row = dict(r)
        try:
            if datetime.strptime(row["date"], "%d.%m.%Y").date() >= today:
                result.append(row)
        except Exception:
            result.append(row)
    return result


async def delete_booking(booking_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
        await db.commit()
        return cursor.rowcount > 0


async def get_bookings(date: Optional[str] = None, limit: int = 50) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if date:
            cursor = await db.execute(
                "SELECT * FROM bookings WHERE date=? ORDER BY time ASC", (date,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM bookings ORDER BY id DESC LIMIT ?", (limit,)
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ── Блокировки от администратора ──────────────────────────────

async def block_slot(date: str, time: Optional[str], reason: Optional[str] = None) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO blocked_slots (date, time, reason) VALUES (?,?,?)",
            (date, time, reason),
        )
        await db.commit()


async def unblock_slot(date: str, time: Optional[str]) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        if time:
            cursor = await db.execute(
                "DELETE FROM blocked_slots WHERE date=? AND time=?", (date, time)
            )
        else:
            cursor = await db.execute(
                "DELETE FROM blocked_slots WHERE date=?", (date,)
            )
        await db.commit()
        return cursor.rowcount


async def unblock_by_id(block_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("DELETE FROM blocked_slots WHERE id=?", (block_id,))
        await db.commit()
        return cursor.rowcount > 0


async def get_blocked_slots(date: str) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM blocked_slots WHERE date=?", (date,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def is_day_blocked(date: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM blocked_slots WHERE date=? AND time IS NULL LIMIT 1", (date,)
        )
        return await cursor.fetchone() is not None


async def get_all_blocked() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM blocked_slots ORDER BY date, time"
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
