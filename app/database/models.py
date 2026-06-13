from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Animal:
    id: str
    name: str
    result_title: str
    description: str
    fact: str
    strengths: str
    motto: str
    guardianship_text: str
    image_filename: str


@dataclass(frozen=True)
class Answer:
    id: str
    question_id: int
    text: str
    position: int


@dataclass(frozen=True)
class Question:
    id: int
    question_type: str
    text: str
    position: int
    answers: list[Answer]


@dataclass(frozen=True)
class QuizProgress:
    telegram_user_id: int
    current_state: str | None
    current_question_position: int
    scores: dict[str, int]
    selected_answers: list[str]
    result_animal_id: str | None
    started_at: str | None
    finished_at: str | None
