from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.models import Answer


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Начать викторину", callback_data="quiz:start")],
        ]
    )


def continue_or_restart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="quiz:continue")],
            [InlineKeyboardButton(text="Начать заново", callback_data="quiz:restart")],
        ]
    )


def question_keyboard(answers: list[Answer]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=answer.text, callback_data=f"quiz:answer:{answer.id}")]
            for answer in answers
        ]
    )


def result_keyboard(share_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Узнать больше об опеке", callback_data="guardianship:more")],
            [InlineKeyboardButton(text="Поделиться результатом", url=share_url)],
            [InlineKeyboardButton(text="Связаться с сотрудником", callback_data="contact:start")],
            [InlineKeyboardButton(text="Оставить отзыв", callback_data="feedback:start")],
            [InlineKeyboardButton(text="Попробовать ещё раз", callback_data="quiz:restart")],
        ]
    )


def completed_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Показать результат", callback_data="result:show")],
            [InlineKeyboardButton(text="Оставить отзыв", callback_data="feedback:start")],
            [InlineKeyboardButton(text="Попробовать ещё раз", callback_data="quiz:restart")],
        ]
    )


def feedback_rating_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=str(value), callback_data=f"feedback:rating:{value}")
                for value in range(1, 6)
            ]
        ]
    )


def feedback_skip_keyboard(skip_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=skip_text, callback_data="feedback:skip")],
        ]
    )
