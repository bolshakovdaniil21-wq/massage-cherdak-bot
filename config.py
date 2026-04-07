# =============================================================
# КОНФИГУРАЦИЯ БОТА — ТЕРРИТОРИЯ МАССАЖА
# =============================================================

BOT_TOKEN = "8599368900:AAGMRWanUHDmyr-3nXFC-C96C1Hv3CaW7Us"
ADMIN_ID   = 890134615

STUDIO_NAME      = "Территория массажа"
ADDRESS          = "г. Подольск, ул. Дружбы, д. 15\nФитнес-студия «Чердак» (кабинет внутри студии)"
PHONE            = "+7 (925) 889-55-72"
TELEGRAM_CONTACT = "@Fakiri19"
WORK_HOURS       = "Ежедневно: 09:00 – 21:00"
MAP_URL          = "https://yandex.ru/maps/?text=Подольск+ул+Дружбы+15"

# =============================================================
# СПЕЦИАЛИСТЫ
# =============================================================

SPECIALISTS = {
    "adjmal": {"id": "adjmal", "name": "Аджмал",  "note": "Массаж"},
    "milana": {"id": "milana", "name": "Милана",  "note": "Массаж + депиляция воском"},
    "both":   {"id": "both",   "name": "Аджмал + Милана", "note": "Массаж в 4 руки"},
}

# =============================================================
# ВРЕМЕННЫЕ СЛОТЫ
# Массаж — каждый час (09:00–20:00)
# Воск   — каждые 30 минут (09:00–20:30)
# =============================================================

MASSAGE_TIME_SLOTS = [
    "09:00", "10:00", "11:00", "12:00", "13:00", "14:00",
    "15:00", "16:00", "17:00", "18:00", "19:00", "20:00",
]

WAX_TIME_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
]

TIME_SLOTS = MASSAGE_TIME_SLOTS  # обратная совместимость

BOOKING_DAYS_AHEAD = 14

# =============================================================
# УСЛУГИ
# slot_type:   "massage" | "wax"
# specialist_id: "adjmal" | "milana" | "both"
# category:    "adjmal" | "milana" | "fourhands" | "wax"
#
# Правила слотов:
#   Массаж: duration ≤ 60 мин = 1 слот (час), 90 мин = 2 слота
#   Воск:   duration ≤ 30 мин = 1 слот (30 мин), 60 мин = 2 слота
#   40/50 мин массаж — закрывают 1 часовой слот (целый час)
# =============================================================

SERVICES = [

    # ── АДЖМАЛ ───────────────────────────────────────────────
    {
        "id": "adj_sport", "category": "adjmal", "slot_type": "massage",
        "name": "Спортивный массаж с элементами растяжки",
        "description": "Глубокая проработка мышц с элементами растяжки.",
        "duration_min": 90, "price": "3 000 ₽",
        "specialist_id": "adjmal",
    },
    {
        "id": "adj_back", "category": "adjmal", "slot_type": "massage",
        "name": "Массаж спины с элементами растяжки",
        "description": "Спина, ШВЗ, руки. Снимает напряжение, улучшает осанку.",
        "duration_min": 50, "price": "2 000 ₽",
        "specialist_id": "adjmal",
    },
    {
        "id": "adj_legs", "category": "adjmal", "slot_type": "massage",
        "name": "Массаж ног с элементами растяжки",
        "description": "Задняя и передняя поверхность ног, стопы.",
        "duration_min": 50, "price": "2 000 ₽",
        "specialist_id": "adjmal",
    },
    {
        "id": "adj_shvz", "category": "adjmal", "slot_type": "massage",
        "name": "Массаж ШВЗ",
        "description": "Шейно-воротниковая зона. Снимает головную боль и напряжение.",
        "duration_min": 40, "price": "1 500 ₽",
        "specialist_id": "adjmal",
    },
    {
        "id": "adj_classic", "category": "adjmal", "slot_type": "massage",
        "name": "Классический массаж тела",
        "description": "Спина, задняя и передняя поверхность ног, живот.",
        "duration_min": 60, "price": "2 000 ₽",
        "specialist_id": "adjmal",
    },
    {
        "id": "adj_anticell_30", "category": "adjmal", "slot_type": "massage",
        "name": "Антицеллюлитный ручной — 30 мин",
        "description": "Интенсивный ручной антицеллюлитный массаж.",
        "duration_min": 30, "price": "1 500 ₽",
        "specialist_id": "adjmal",
    },
    {
        "id": "adj_anticell_60", "category": "adjmal", "slot_type": "massage",
        "name": "Антицеллюлитный ручной — 60 мин",
        "description": "Интенсивный ручной антицеллюлитный массаж.",
        "duration_min": 60, "price": "2 500 ₽",
        "specialist_id": "adjmal",
    },

    # ── МИЛАНА (массаж) ───────────────────────────────────────
    {
        "id": "mil_caramel", "category": "milana", "slot_type": "massage",
        "name": "Карамельная липосакция с обёртыванием",
        "description": "Массаж + обёртывание. Коррекция фигуры, подтяжка кожи.",
        "duration_min": 60, "price": "2 000 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_lymph", "category": "milana", "slot_type": "massage",
        "name": "Лимфодренажный массаж",
        "description": "Убирает отёки, выводит токсины, улучшает лимфоток.",
        "duration_min": 60, "price": "2 300 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_honey", "category": "milana", "slot_type": "massage",
        "name": "Медовый массаж",
        "description": "Детокс, улучшение тонуса и цвета кожи.",
        "duration_min": 60, "price": "1 500 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_fullbody", "category": "milana", "slot_type": "massage",
        "name": "Общий массаж тела",
        "description": "Комплексный массаж всего тела. Полное восстановление.",
        "duration_min": 90, "price": "2 700 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_buccal", "category": "milana", "slot_type": "massage",
        "name": "Буккальный массаж лица",
        "description": "Работа с мышцами лица изнутри. Лифтинг-эффект.",
        "duration_min": 60, "price": "2 000 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_modeling", "category": "milana", "slot_type": "massage",
        "name": "Моделирование тела",
        "description": "Коррекция и моделирование контуров тела.",
        "duration_min": 90, "price": "5 000 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_head", "category": "milana", "slot_type": "massage",
        "name": "Массаж головы",
        "description": "Расслабляющий массаж кожи головы. Снимает стресс, улучшает сон.",
        "duration_min": 30, "price": "1 200 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_head_shvz", "category": "milana", "slot_type": "massage",
        "name": "Массаж головы и ШВЗ",
        "description": "Комплекс: шейно-воротниковая зона + голова. Снимает мигрени.",
        "duration_min": 60, "price": "2 500 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_feet", "category": "milana", "slot_type": "massage",
        "name": "Стопы",
        "description": "Расслабляющий массаж стоп. Снимает усталость.",
        "duration_min": 60, "price": "1 400 ₽",
        "specialist_id": "milana",
    },
    {
        "id": "mil_face", "category": "milana", "slot_type": "massage",
        "name": "Массаж лица",
        "description": "Расслабляющий и омолаживающий массаж лица.",
        "duration_min": 60, "price": "1 200 ₽",
        "specialist_id": "milana",
    },

    # ── ОБЩАЯ (Аджмал + Милана) ───────────────────────────────
    {
        "id": "fourhands", "category": "fourhands", "slot_type": "massage",
        "name": "Массаж в 4 руки",
        "description": "Аджмал и Милана работают одновременно. Уникальный расслабляющий эффект.",
        "duration_min": 60, "price": "3 000 ₽",
        "specialist_id": "both",
    },

    # ── ДЕПИЛЯЦИЯ ВОСКОМ (Милана, ТОЛЬКО ДЛЯ ЖЕНЩИН) ─────────
    {
        "id": "wax_armpit", "category": "wax", "slot_type": "wax",
        "name": "Подмышки",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "от 350 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_hips", "category": "wax", "slot_type": "wax",
        "name": "Бёдра",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "700 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_shins", "category": "wax", "slot_type": "wax",
        "name": "Голени",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "700 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_lower_back", "category": "wax", "slot_type": "wax",
        "name": "Поясница",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "500 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_glutes", "category": "wax", "slot_type": "wax",
        "name": "Ягодицы",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "500 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_lip", "category": "wax", "slot_type": "wax",
        "name": "Верхняя губа",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "200 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_bikini", "category": "wax", "slot_type": "wax",
        "name": "Глубокое бикини",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "2 000 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_full_legs", "category": "wax", "slot_type": "wax",
        "name": "Ноги полностью",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "1 100 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_full_arms", "category": "wax", "slot_type": "wax",
        "name": "Руки полностью",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "800 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_skins", "category": "wax", "slot_type": "wax",
        "name": "Skin's глубокое бикини",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 20, "price": "2 000 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_complex1", "category": "wax", "slot_type": "wax",
        "name": "Комплекс: подмышки + ноги полностью + глубокое бикини",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 60, "price": "от 3 200 ₽",
        "specialist_id": "milana", "women_only": True,
    },
    {
        "id": "wax_complex2", "category": "wax", "slot_type": "wax",
        "name": "Комплекс: подмышки + голени + глубокое бикини",
        "description": "⚠️ УСЛУГА ТОЛЬКО ДЛЯ ЖЕНЩИН",
        "duration_min": 60, "price": "от 2 600 ₽",
        "specialist_id": "milana", "women_only": True,
    },
]

SERVICES_BY_ID: dict = {s["id"]: s for s in SERVICES}
