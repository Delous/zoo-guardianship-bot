from __future__ import annotations

import sqlite3
from typing import Any


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS animals (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    result_title TEXT NOT NULL,
    description TEXT NOT NULL,
    fact TEXT NOT NULL,
    strengths TEXT NOT NULL,
    motto TEXT NOT NULL,
    guardianship_text TEXT NOT NULL,
    image_filename TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    question_type TEXT NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS answers (
    id TEXT PRIMARY KEY,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS answer_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    answer_id TEXT NOT NULL,
    animal_id TEXT NOT NULL,
    score INTEGER NOT NULL,
    FOREIGN KEY (answer_id) REFERENCES answers(id) ON DELETE CASCADE,
    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS static_texts (
    key TEXT PRIMARY KEY,
    text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_quiz_progress (
    telegram_user_id INTEGER PRIMARY KEY,
    current_state TEXT,
    current_question_position INTEGER NOT NULL DEFAULT 1,
    scores_json TEXT NOT NULL DEFAULT '{}',
    selected_answers_json TEXT NOT NULL DEFAULT '[]',
    fsm_data_json TEXT NOT NULL DEFAULT '{}',
    result_animal_id TEXT,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_animal_id) REFERENCES animals(id)
);

CREATE TABLE IF NOT EXISTS contact_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    full_name TEXT,
    username TEXT,
    result_animal_id TEXT,
    question_text TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_animal_id) REFERENCES animals(id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id INTEGER NOT NULL,
    full_name TEXT,
    username TEXT,
    result_animal_id TEXT,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_animal_id) REFERENCES animals(id)
);
"""


ANIMALS: list[dict[str, Any]] = [
    {
        "id": "manul",
        "name": "Манул",
        "result_title": "Ваше тотемное животное — Манул.",
        "description": (
            "Вы — человек с мощной внутренней независимостью и лицом, на котором иногда "
            "написано: Я всё понял, но участвовать не обещал. Вы цените личное пространство, "
            "не любите лишнюю суету и умеете быть невероятно обаятельным именно тогда, когда "
            "ничего специально для этого не делаете.\n\n"
            "Манул — символ самостоятельности, спокойного достоинства и умения жить по своим правилам."
        ),
        "fact": "Манулы обладают очень густым мехом: на одном квадратном сантиметре кожи может быть до девяти тысяч волосков.",
        "strengths": "независимость, гордость, устойчивость к драмам",
        "motto": "Я не холодный, я просто экономлю социальную батарейку.",
        "guardianship_text": (
            "Опека помогает Московскому зоопарку заботиться о животных, их питании, "
            "условиях содержания и благополучии."
        ),
        "image_filename": "manul.jpg",
    },
    {
        "id": "capybara",
        "name": "Капибара",
        "result_title": "Ваше тотемное животное — Капибара.",
        "description": (
            "Вы — человек спокойствия. Рядом с вами мир перестаёт быть суетливым, "
            "люди вспоминают, что можно не бежать, а проблемы выглядят чуть менее катастрофично.\n\n"
            "Капибара — символ спокойствия, дружелюбия и внутренней устойчивости."
        ),
        "fact": "Капибары хорошо плавают, а их глаза, уши и ноздри расположены высоко, чтобы животное могло наблюдать из воды.",
        "strengths": "умение сглаживать напряжение, доброжелательность, спокойная уверенность",
        "motto": "Паника отменяется, сначала просто посидим.",
        "guardianship_text": "Программа опеки — способ регулярно помогать животным и поддерживать работу зоопарка.",
        "image_filename": "capybara.jpg",
    },
    {
        "id": "raccoon",
        "name": "Енот",
        "result_title": "Ваше тотемное животное — Енот.",
        "description": (
            "Вы — исследователь всего странного, интересного и потенциально полезного. "
            "У вас талант находить детали, которые другие не заметили, и превращать обычную "
            "ситуацию в приключение.\n\n"
            "Енот — символ любопытства, гибкости и лёгкого творческого хаоса."
        ),
        "fact": "У енотов очень чувствительные передние лапы: с их помощью они изучают предметы почти как руками.",
        "strengths": "находчивость, живой ум, чувство юмора",
        "motto": "Я просто посмотрю и не буду ничего трогать. Наверное.",
        "guardianship_text": "Программа опеки помогает направить энергию в полезное дело: животным нужна постоянная забота.",
        "image_filename": "raccoon.jpg",
    },
    {
        "id": "flamingo",
        "name": "Фламинго",
        "result_title": "Ваше тотемное животное — Фламинго.",
        "description": (
            "Вы умеете добавлять миру выразительности. Даже если день серый, вы способны найти "
            "в нём красивый ракурс, интересную деталь или достойный повод надеть что-то приятное.\n\n"
            "Фламинго — символ яркости, изящества и внутреннего стиля."
        ),
        "fact": "Розовый цвет фламинго связан с каротиноидами в пище; птенцы появляются на свет сероватыми.",
        "strengths": "чувство эстетики, умение создавать настроение, способность выделяться",
        "motto": "Да, ситуация сложная. Но я всё равно выйду из неё красиво.",
        "guardianship_text": "Опека даёт возможность поддержать ярких обитателей зоопарка и стать частью заботы о них.",
        "image_filename": "flamingo.jpg",
    },
    {
        "id": "eagle_owl",
        "name": "Филин",
        "result_title": "Ваше тотемное животное — Филин.",
        "description": (
            "Вы — человек, который замечает больше, чем говорит. Пока остальные обсуждают очевидное, "
            "вы уже начинаете понимать причины и последствия.\n\n"
            "Филин — символ мудрости, внимательности и спокойного анализа."
        ),
        "fact": "Филины способны почти бесшумно летать благодаря особому строению перьев.",
        "strengths": "наблюдательность, аналитическое мышление, выдержка",
        "motto": "Я пока молчу, но у меня уже есть схема.",
        "guardianship_text": "Программа опеки помогает поддержать животных, которые часто остаются за кадром повседневного внимания.",
        "image_filename": "eagle_owl.jpg",
    },
]


QUESTIONS: list[dict[str, Any]] = [
    {
        "id": 1,
        "position": 1,
        "question_type": "work_life",
        "text": "Утро понедельника. Ваш внутренний зверь первым делом…",
        "answers": [
            {"id": "q1_a", "text": "Открывает один глаз и оценивает, достоин ли мир его присутствия.", "scores": {"manul": 1}},
            {"id": "q1_b", "text": "Спокойно принимает реальность. Понедельник так понедельник. Главное — не суетиться.", "scores": {"capybara": 1}},
            {"id": "q1_c", "text": "Уже что-то ищет: зарядку, ключи, смысл жизни, вчерашний бутерброд.", "scores": {"raccoon": 1}},
            {"id": "q1_d", "text": "Появляется красиво, даже если внутри полный раздрай.", "scores": {"flamingo": 1}},
            {"id": "q1_e", "text": "Молча наблюдает за происходящим и делает выводы. Очень точные.", "scores": {"eagle_owl": 1}},
        ],
    },
    {
        "id": 2,
        "position": 2,
        "question_type": "work_life",
        "text": "На работе внезапно появился срочный проект. Ваша реакция:",
        "answers": [
            {"id": "q2_a", "text": "Я в этом не участвую эмоционально, но физически, видимо, придётся.", "scores": {"manul": 1}},
            {"id": "q2_b", "text": "Давайте спокойно разберёмся. Паника — не самый эффективный процесс.", "scores": {"capybara": 1}},
            {"id": "q2_c", "text": "Я сначала посмотрю, что лежит в папке “Финал_точно_последний_версия7”?", "scores": {"raccoon": 1}},
            {"id": "q2_d", "text": "Хорошо, но презентация должна выглядеть прилично. Мы же не дикари.", "scores": {"flamingo": 1}},
            {"id": "q2_e", "text": "Я уже понял, что в третьем пункте есть проблема, но пока думаю про себя как её решить.", "scores": {"eagle_owl": 1}},
        ],
    },
    {
        "id": 3,
        "position": 3,
        "question_type": "personality",
        "text": "Ваш идеальный выходной:",
        "answers": [
            {"id": "q3_a", "text": "Никто меня не трогает. Я никого не трогаю. Высшая форма гармонии.", "scores": {"manul": 1}},
            {"id": "q3_b", "text": "Вкусная еда, мягкий плед, приятные люди рядом.", "scores": {"capybara": 1}},
            {"id": "q3_c", "text": "Сходить просто посмотреть и вернуться с пятью неожиданными покупками и новой историей.", "scores": {"raccoon": 1}},
            {"id": "q3_d", "text": "Прогулка, красивое место, фото, кофе, ощущение: я персонаж приятного фильма.", "scores": {"flamingo": 1}},
            {"id": "q3_e", "text": "Книга, тишина, чай и возможность не объяснять, почему это лучший план.", "scores": {"eagle_owl": 1}},
        ],
    },
    {
        "id": 4,
        "position": 4,
        "question_type": "humor",
        "text": "Если бы у вас был личный девиз, он звучал бы так:",
        "answers": [
            {"id": "q4_a", "text": "Не подходи — и мы прекрасно поладим.", "scores": {"manul": 1}},
            {"id": "q4_b", "text": "Мир не рухнет, если немного посидеть у воды.", "scores": {"capybara": 1}},
            {"id": "q4_c", "text": "Я не хаос. Я исследователь альтернативных порядков.", "scores": {"raccoon": 1}},
            {"id": "q4_d", "text": "Даже если всё сложно, можно быть красивым.", "scores": {"flamingo": 1}},
            {"id": "q4_e", "text": "Сначала подумай. Потом ещё раз подумай. Потом уже можно говорить.", "scores": {"eagle_owl": 1}},
        ],
    },
    {
        "id": 5,
        "position": 5,
        "question_type": "general",
        "text": "Как вы ведёте себя в компании?",
        "answers": [
            {"id": "q5_a", "text": "Сначала держусь на дистанции. Потом, возможно, разрешаю себя любить.", "scores": {"manul": 1}},
            {"id": "q5_b", "text": "Становлюсь спокойным центром компании. Со мной всем чуть легче дышать.", "scores": {"capybara": 1}},
            {"id": "q5_c", "text": "Завожу странные разговоры, нахожу смешные детали, случайно становлюсь душой вечера.", "scores": {"raccoon": 1}},
            {"id": "q5_d", "text": "Люблю атмосферу, красивые детали и моменты, когда всё выглядит как надо.", "scores": {"flamingo": 1}},
            {"id": "q5_e", "text": "Больше слушаю, чем говорю. Зато потом выдаю одну фразу, после которой все задумываются.", "scores": {"eagle_owl": 1}},
        ],
    },
    {
        "id": 6,
        "position": 6,
        "question_type": "animal_fact",
        "text": "Вам подарили возможность стать опекуном животного. Вы выбираете того, кто…",
        "answers": [
            {"id": "q6_a", "text": "Самобытный, независимый и немного похож на живой мем с серьёзным лицом.", "scores": {"manul": 1}},
            {"id": "q6_b", "text": "Спокойный, дружелюбный и умеет напоминать людям: выдохни.", "scores": {"capybara": 1}},
            {"id": "q6_c", "text": "Любопытный, ловкий и явно знает, где лежит всё интересное.", "scores": {"raccoon": 1}},
            {"id": "q6_d", "text": "Яркий, необычный и добавляет миру немного театральности.", "scores": {"flamingo": 1}},
            {"id": "q6_e", "text": "Мудрый, внимательный и смотрит так, будто уже прочитал вашу биографию.", "scores": {"eagle_owl": 1}},
        ],
    },
    {
        "id": 7,
        "position": 7,
        "question_type": "personality",
        "text": "Какой ваш главный суперскилл?",
        "answers": [
            {"id": "q7_a", "text": "Сохранять личные границы даже взглядом.", "scores": {"manul": 1}},
            {"id": "q7_b", "text": "Делать дружелюбным пространство вокруг себя.", "scores": {"capybara": 1}},
            {"id": "q7_c", "text": "Находить странные, нестандартные, но эффективные решения.", "scores": {"raccoon": 1}},
            {"id": "q7_d", "text": "Создавать настроение и красоту даже в обычном дне.", "scores": {"flamingo": 1}},
            {"id": "q7_e", "text": "Видеть суть, пока остальные спорят о деталях.", "scores": {"eagle_owl": 1}},
        ],
    },
]


STATIC_TEXTS: dict[str, str] = {
    "quiz_title": "Какое у вас тотемное животное?",
    "start": (
        "Привет! Это викторина Московского зоопарка о программе опеки.\n\n"
        "Ответьте на несколько вопросов — и бот подберёт животное, которое ближе вам по характеру. "
        "В финале вы узнаете результат, факт о животном и как можно поддержать обитателей зоопарка."
    ),
    "before_questions": "Отвечайте честно: здесь нет правильных и неправильных вариантов.",
    "before_result": "Готово! Мы посчитали баллы и нашли ваше тотемное животное.",
    "guardianship_full": (
        "Программа опеки Московского зоопарка — это возможность поддержать конкретное животное. "
        "Опекуны помогают обеспечивать питание, уход, обогащение среды и комфортные условия жизни.\n\n"
        "Животное остаётся жить в зоопарке, а вы становитесь участником важной регулярной заботы."
    ),
    "share_text_template": (
        "Мой результат в викторине Московского зоопарка — {animal_name}.\n\n"
        "Пройди тоже и узнай своё тотемное животное"
    ),
    "contact_intro": "Напишите ваш вопрос о программе опеки. Я передам его сотруднику вместе с вашим результатом.",
    "contact_success": "Спасибо! Ваш вопрос сохранён и отправлен сотруднику.",
    "feedback_intro": "Оцените, пожалуйста, викторину от 1 до 5.",
    "feedback_comment_request": "Хотите оставить короткий комментарий? Можно написать текст или нажать «Пропустить».",
    "feedback_success": "Спасибо за отзыв! Он сохранён.",
    "fallback": "Пожалуйста, выберите действие кнопкой. Так бот поймёт, что нужно сделать дальше.",
    "continue_or_restart": "Вы уже начали викторину. Хотите продолжить с текущего вопроса или начать заново?",
    "completed_actions": "Вы уже завершили викторину. Можно посмотреть результат, оставить отзыв или пройти ещё раз.",
    "restart": "Начинаем заново!",
    "no_comment": "Пропустить",
}


def create_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_SQL)
    connection.commit()


def table_has_data(connection: sqlite3.Connection, table_name: str) -> bool:
    cursor = connection.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
    return cursor.fetchone() is not None


def seed_database(connection: sqlite3.Connection) -> None:
    if table_has_data(connection, "animals"):
        return

    connection.executemany(
        """
        INSERT INTO animals (
            id, name, result_title, description, fact, strengths, motto, guardianship_text, image_filename
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        [
            (
                animal["id"],
                animal["name"],
                animal["result_title"],
                animal["description"],
                animal["fact"],
                animal["strengths"],
                animal["motto"],
                animal["guardianship_text"],
                animal["image_filename"],
            )
            for animal in ANIMALS
        ],
    )

    for question in QUESTIONS:
        connection.execute(
            "INSERT INTO questions (id, question_type, text, position) VALUES (?, ?, ?, ?);",
            (question["id"], question["question_type"], question["text"], question["position"]),
        )
        for position, answer in enumerate(question["answers"], start=1):
            connection.execute(
                "INSERT INTO answers (id, question_id, text, position) VALUES (?, ?, ?, ?);",
                (answer["id"], question["id"], answer["text"], position),
            )
            for animal_id, score in answer["scores"].items():
                connection.execute(
                    "INSERT INTO answer_scores (answer_id, animal_id, score) VALUES (?, ?, ?);",
                    (answer["id"], animal_id, score),
                )

    connection.executemany("INSERT INTO static_texts (key, text) VALUES (?, ?);", STATIC_TEXTS.items())
    connection.commit()
