from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    answering = State()
    completed = State()


class ContactStates(StatesGroup):
    waiting_question = State()


class FeedbackStates(StatesGroup):
    waiting_rating = State()
    waiting_comment = State()
