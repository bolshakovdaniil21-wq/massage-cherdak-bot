"""
Логика доступности временных слотов. Один кабинет.

ПРАВИЛА БЛОКИРОВКИ:

Воск (слот 30 мин, сеанс 20 мин):
  - 1 воск-слот (9:00) → закрывает: воск 9:00 + массаж 9:00
  - 2 воск-слота (9:00+9:30, комплекс) → закрывает: воск 9:00, 9:30 + массаж 9:00

Массаж ≤60 мин (1 слот):
  - 9:00 → закрывает: массаж 9:00 + воск 9:00, 9:30

Массаж 90 мин (2 слота):
  - 9:00 → закрывает: массаж 9:00, 10:00 + воск 9:00, 9:30, 10:00, 10:30
"""

from config import MASSAGE_TIME_SLOTS, WAX_TIME_SLOTS
from database import get_all_bookings_for_date, get_blocked_slots, get_bookings_for_specialist, is_day_blocked


def _hour(time_str: str) -> int:
    return int(time_str.split(":")[0])


def _massage_blocked_by_wax(wax_time: str) -> str:
    """Любой воск-слот → закрывает часовой слот массажа того же часа."""
    return f"{_hour(wax_time):02d}:00"


def _wax_blocked_by_massage(massage_time: str, duration_min: int) -> list:
    """Массаж → закрывает :00 и :30 каждого часа, который занимает."""
    h = _hour(massage_time)
    hours = 1 if duration_min <= 60 else 2
    result = []
    for i in range(hours):
        s = f"{h + i:02d}:00"
        half = f"{h + i:02d}:30"
        if s in WAX_TIME_SLOTS:
            result.append(s)
        if half in WAX_TIME_SLOTS:
            result.append(half)
    return result


async def get_available_slots(
    specialist_id: str,
    date: str,
    duration_min: int,
    slot_type: str = "massage",
) -> list:

    if await is_day_blocked(date):
        return []

    admin_blocks = await get_blocked_slots(date)

    # ── WAX ──────────────────────────────────────────────────
    if slot_type == "wax":
        # Один кабинет: смотрим ВСЕ записи на дату, независимо от специалиста
        bookings = await get_all_bookings_for_date(date)
        blocked: set = set()

        for b in bookings:
            t, dur, btype = b["time"], b["duration_min"], b.get("slot_type", "massage")
            if btype == "wax":
                # Воск блокирует только свой конкретный слот
                if t in WAX_TIME_SLOTS:
                    blocked.add(t)
            else:
                # Массаж → закрывает :00 и :30 своих часов
                blocked.update(_wax_blocked_by_massage(t, dur))

        for ab in admin_blocks:
            if not ab["time"]:
                return []
            t = ab["time"]
            if t in WAX_TIME_SLOTS:
                blocked.add(t)
            elif t in MASSAGE_TIME_SLOTS:
                blocked.update(_wax_blocked_by_massage(t, 60))

        # Сколько восковых слотов нужно подряд (каждые 30 мин)
        wax_n = max(1, duration_min // 30)
        available = []
        for i, slot in enumerate(WAX_TIME_SLOTS):
            free = all(
                (i + j) < len(WAX_TIME_SLOTS) and WAX_TIME_SLOTS[i + j] not in blocked
                for j in range(wax_n)
            )
            if free:
                available.append(slot)
        return available

    # ── MASSAGE ───────────────────────────────────────────────
    else:
        bookings = await get_bookings_for_specialist(specialist_id, date)
        blocked: set = set()

        for b in bookings:
            t, dur, btype = b["time"], b["duration_min"], b.get("slot_type", "massage")
            if btype == "massage":
                # Массаж блокирует свои часовые слоты
                massage_n = 1 if dur <= 60 else 2
                if t in MASSAGE_TIME_SLOTS:
                    idx = MASSAGE_TIME_SLOTS.index(t)
                    for j in range(massage_n):
                        if idx + j < len(MASSAGE_TIME_SLOTS):
                            blocked.add(MASSAGE_TIME_SLOTS[idx + j])
            else:
                # Любой воск → закрывает часовой слот массажа того же часа
                blocked.add(_massage_blocked_by_wax(t))

        for ab in admin_blocks:
            if not ab["time"]:
                return []
            t = ab["time"]
            if t in MASSAGE_TIME_SLOTS:
                blocked.add(t)
            elif t in WAX_TIME_SLOTS:
                blocked.add(_massage_blocked_by_wax(t))

        massage_n = 1 if duration_min <= 60 else 2
        available = []
        for i, slot in enumerate(MASSAGE_TIME_SLOTS):
            free = all(
                (i + j) < len(MASSAGE_TIME_SLOTS) and MASSAGE_TIME_SLOTS[i + j] not in blocked
                for j in range(massage_n)
            )
            if free:
                available.append(slot)
        return available
