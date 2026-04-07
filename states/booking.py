from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    choosing_category = State()  # 1: категория
    choosing_service  = State()  # 2: услуга
    entering_name     = State()  # 3: имя
    entering_phone    = State()  # 4: телефон
    choosing_date     = State()  # 5: дата
    choosing_time     = State()  # 6: время
    entering_comment  = State()  # 7: комментарий
    confirming        = State()  # 8: подтверждение
