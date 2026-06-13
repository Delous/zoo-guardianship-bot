from __future__ import annotations

from pathlib import Path

from aiogram import Dispatcher

from app.bot.sqlite_storage import SQLiteStorage
from app.config import Settings
from app.handlers import contact, fallback, feedback, guardianship, quiz, result, start
from app.repositories.animal_repository import AnimalRepository
from app.repositories.contact_repository import ContactRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.user_repository import UserRepository
from app.services.contact_service import ContactService
from app.services.feedback_service import FeedbackService
from app.services.quiz_service import QuizService
from app.services.result_service import ResultService
from app.services.sharing_service import SharingService


def build_dispatcher(settings: Settings) -> Dispatcher:
    storage = SQLiteStorage(settings.database_path)
    dp = Dispatcher(storage=storage)

    animals = AnimalRepository(settings.database_path)
    questions = QuestionRepository(settings.database_path)
    users = UserRepository(settings.database_path)
    contacts = ContactRepository(settings.database_path)
    feedback_repo = FeedbackRepository(settings.database_path)

    media_dir = Path(__file__).resolve().parents[2] / "media" / "animals"

    dp["animal_repository"] = animals
    dp["quiz_service"] = QuizService(questions, users)
    dp["result_service"] = ResultService(animals, users, media_dir)
    dp["sharing_service"] = SharingService(animals, settings.bot_link)
    dp["contact_service"] = ContactService(contacts, settings.admin_chat_id)
    dp["feedback_service"] = FeedbackService(feedback_repo)

    dp.include_router(start.router)
    dp.include_router(quiz.router)
    dp.include_router(result.router)
    dp.include_router(guardianship.router)
    dp.include_router(contact.router)
    dp.include_router(feedback.router)
    dp.include_router(fallback.router)
    return dp
