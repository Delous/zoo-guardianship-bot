from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

from app.bot.states import QuizStates
from app.database.models import Animal
from app.keyboards.inline import result_keyboard
from app.services.result_service import ResultService
from app.services.sharing_service import SharingService


router = Router()
logger = logging.getLogger(__name__)


async def send_result(
    message: Message,
    animal: Animal,
    result_service: ResultService,
    sharing_service: SharingService,
) -> None:
    share_url = await sharing_service.build_share_url(animal)
    image_path = result_service.image_path_for(animal)
    if image_path.exists():
        await message.answer_photo(FSInputFile(image_path))
    else:
        logger.warning("Animal image is missing: %s", image_path)

    await message.answer(
        await result_service.format_result_text(animal),
        reply_markup=result_keyboard(share_url),
    )


@router.callback_query(F.data == "result:show")
async def show_result(
    callback: CallbackQuery,
    result_service: ResultService,
    sharing_service: SharingService,
) -> None:
    animal = await result_service.get_or_create_result(callback.from_user.id, QuizStates.completed.state)
    await send_result(callback.message, animal, result_service, sharing_service)
    await callback.answer()
