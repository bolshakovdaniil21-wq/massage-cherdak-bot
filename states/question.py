from aiogram.fsm.state import State, StatesGroup


class QuestionStates(StatesGroup):
    entering_question = State()
