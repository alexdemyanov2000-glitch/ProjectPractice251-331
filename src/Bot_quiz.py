import logging
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from telegram.ext import ApplicationBuilder
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

START_QUIZ, ANSWER = range(2)

ALL_QUESTIONS = [
    {
        "question": "Сколько дней длилась блокада Ленинграда?",
        "options": ["600 дней", "872 дня", "900 дней", "1000 дней"],
        "answer": "872 дня"
    },
    {
        "question": "Сколько длилась Сталинградская битва?",
        "options": ["100 дней", "125 дней", "200 дней", "250 дней"],
        "answer": "200 дней"
    },
    {
        "question": "Как называлась операция по освобождению Беларуси летом 1944 года?",
        "options": ["Багратион", "Кутузов", "Уран", "Цитадель"],
        "answer": "Багратион"
    },
    {
        "question": "Самый молодой Герой Советского Союза, погибший в 15 лет, закрыв собой амбразуру вражеского дзота?",
        "options": ["Александр Матросов", "Марат Казей", "Валя Котик", "Лёня Голиков"],
        "answer": "Александр Матросов"
    },
    {
        "question": "Назовите советский танк, признанный лучшим танком Второй мировой войны?",
        "options": ["Т-34", "КВ-1", "ИС-2", "Т-70"],
        "answer": "Т-34"
    },
    {
        "question": "Какой город во время ВОВ выдержал осаду немецких войск в течение 250 дней, но так и не был сдан?",
        "options": ["Одесса", "Киев", "Севастополь", "Минск"],
        "answer": "Севастополь"
    },
    {
        "question": "Кто командовал Парадом Победы на Красной площади 24 июня 1945 года?",
        "options": ["Г.К. Жуков", "К.К. Рокоссовский", "И.В. Сталин", "С.М. Будённый"],
        "answer": "К.К. Рокоссовский"
    },
    {
        "question": "Как называлась последняя стратегическая операция Красной Армии, завершившая войну?",
        "options": ["Висло-Одерская", "Берлинская", "Пражская", "Восточно-Прусская"],
        "answer": "Берлинская"
    },
    {
        "question": "В каком году началась Курская битва?",
        "options": ["1941", "1942", "1943", "1944"],
        "answer": "1943"
    },
    {
        "question": "Знаменитый лозунг 'Ни шагу назад!' был введён приказом №227, изданным в:",
        "options": ["Июле 1942", "Августе 1941", "Сентябре 1943", "Марте 1945"],
        "answer": "Июле 1942"
    },
    {
        "question": "Как назывался советский реактивный миномёт, который немцы прозвали 'чёртова метла'?",
        "options": ["Катюша", "Андрюша", "Любаша", "Ванюша"],
        "answer": "Катюша"
    },
    {
        "question": "Кто был Верховным Главнокомандующим СССР в годы Великой Отечественной войны?",
        "options": ["Г.К. Жуков", "И.В. Сталин", "В.М. Молотов", "Л.П. Берия"],
        "answer": "И.В. Сталин"
    },
    {
        "question": "На какой реке произошла встреча советских и американских войск в 1945 году?",
        "options": ["Эльба", "Рейн", "Дунай", "Одер"],
        "answer": "Эльба"
    },
    {
        "question": "Сколько дней длилась Битва за Москву?",
        "options": ["150 дней", "203 дня", "250 дней", "300 дней"],
        "answer": "203 дня"
    },
    {
        "question": "Какой город был захвачен немецкими войсками первым в начале войны?",
        "options": ["Киев", "Минск", "Смоленск", "Львов"],
        "answer": "Минск"
    },
    {
        "question": "Кто совершил первый ночной таран в небе Москвы?",
        "options": ["В. Талалихин", "А. Матросов", "Н. Гастелло", "И. Кожедуб"],
        "answer": "В. Талалихин"
    },
    {
        "question": "Какое звание присваивалось городам за массовый героизм защитников?",
        "options": ["Город-герой", "Город воинской славы", "Город-крепость", "Город победитель"],
        "answer": "Город-герой"
    },
    {
        "question": "Сколько всего городов-героев было в СССР?",
        "options": ["10 городов", "12 городов", "13 городов", "15 городов"],
        "answer": "13 городов"
    },
    {
        "question": "Кто водрузил Знамя Победы над Рейхстагом?",
        "options": ["Егоров и Кантария", "Берест и Самсонов", "Неустроев и Артамонов", "Зинченко и Давыдов"],
        "answer": "Егоров и Кантария"
    },
    {
        "question": "Какой подвиг совершил Александр Матросов?",
        "options": ["Закрыл амбразуру своим телом", "Сбил немецкий самолёт тараном", "Подорвал танк с гранатой",
                    "Повторил подвиг Гастелло"],
        "answer": "Закрыл амбразуру своим телом"
    }
]


MAX_WRONG_ANSWERS = 3
QUESTIONS_PER_GAME = 10


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    keyboard = [[KeyboardButton("Начать квиз")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Здравствуйте, {user.first_name}! Вы готовы начать квиз "
        "на знание различных событий Великой Отечественной Войны?\n\n"
        f"Вас ожидает {QUESTIONS_PER_GAME} случайных вопросов из {len(ALL_QUESTIONS)}.",
        reply_markup=reply_markup
    )
    return START_QUIZ


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    questions_for_game = random.sample(ALL_QUESTIONS, QUESTIONS_PER_GAME)

    context.user_data["questions"] = questions_for_game
    context.user_data["current_question"] = 0
    context.user_data["correct_answers"] = 0
    context.user_data["wrong_answers"] = 0

    await ask_question(update, context)
    return ANSWER


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_index = context.user_data["current_question"]
    questions_list = context.user_data["questions"]

    if q_index >= len(questions_list):
        await finish_quiz_success(update, context)
        return

    question_data = questions_list[q_index]
    question_text = question_data["question"]
    options = question_data["options"]

    shuffled_options = options.copy()
    random.shuffle(shuffled_options)

    context.user_data["shuffled_options"] = shuffled_options
    context.user_data["current_question_data"] = question_data

    keyboard = [
        [KeyboardButton(shuffled_options[0]), KeyboardButton(shuffled_options[1])],
        [KeyboardButton(shuffled_options[2]), KeyboardButton(shuffled_options[3])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Вопрос {q_index + 1} из {len(questions_list)}:\n\n{question_text}",
        reply_markup=reply_markup
    )


async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверяет ответ пользователя."""
    user_answer = update.message.text
    question_data = context.user_data["current_question_data"]
    correct_answer = question_data["answer"]

    if user_answer == correct_answer:
        context.user_data["correct_answers"] += 1
        await update.message.reply_text(f"Верно! {correct_answer} — правильный ответ.")

        context.user_data["current_question"] += 1

        if context.user_data["current_question"] >= len(context.user_data["questions"]):
            await finish_quiz_success(update, context)
            return ConversationHandler.END
        else:
            await ask_question(update, context)
            return ANSWER
    else:
        context.user_data["wrong_answers"] += 1
        wrong_count = context.user_data["wrong_answers"]

        await update.message.reply_text(
            f"Неверно. Правильный ответ: {correct_answer}\n"
            f"Ошибок: {wrong_count}/{MAX_WRONG_ANSWERS}"
        )

        if context.user_data["wrong_answers"] >= MAX_WRONG_ANSWERS:
            await update.message.reply_text(
                "Вы набрали 3 неверных ответа. Прогресс обнуляется.\n"
                "Начинаем квиз заново с новыми вопросами!"
            )
            questions_for_game = random.sample(ALL_QUESTIONS, QUESTIONS_PER_GAME)
            context.user_data["questions"] = questions_for_game
            context.user_data["current_question"] = 0
            context.user_data["correct_answers"] = 0
            context.user_data["wrong_answers"] = 0
            await ask_question(update, context)
            return ANSWER
        else:
            shuffled_options = context.user_data["shuffled_options"]

            keyboard = [
                [KeyboardButton(shuffled_options[0]), KeyboardButton(shuffled_options[1])],
                [KeyboardButton(shuffled_options[2]), KeyboardButton(shuffled_options[3])]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "Попробуйте ответить на этот вопрос ещё раз:",
                reply_markup=reply_markup
            )
            return ANSWER


async def finish_quiz_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    correct = context.user_data.get("correct_answers", 0)
    total = len(context.user_data.get("questions", []))

    await update.message.reply_text(
        f"ПОЗДРАВЛЯЮ!\n"
        f"Вы правильно ответили на все {correct} из {total} вопросов!\n\n"
        f"Вы настоящий знаток истории Великой Отечественной войны!\n"
        f"Хотите пройти квиз ещё раз? Нажмите /start"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена квиза."""
    await update.message.reply_text(
        "Квиз прерван. Если захотите начать заново, нажмите /start"
    )
    return ConversationHandler.END


def main():
   
    TOKEN = "8613966571:AAEI-DHD5-Ipq7kaLIu0fcyXV-XWj93h878"

    
    if TOKEN == "ВАШ_ТОКЕН_ТЕЛЕГРАМ_БОТА":
        print("ОШИБКА: Вы не вставили токен бота!")
        print("Получите токен у @BotFather и замените 'ВАШ_ТОКЕН_ТЕЛЕГРАМ_БОТА' на ваш токен.")
        return

    
    application = Application.builder().token(TOKEN).build()

  
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_QUIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_quiz)],
            ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

   
    print("Бот 'Квиз героизма' запущен...")
    print(f"Всего вопросов в базе: {len(ALL_QUESTIONS)}")
    print(f"За игру выдаётся: {QUESTIONS_PER_GAME} случайных вопросов")
    print("Доступные команды: /start, /cancel")
    print("Бот готов к работе! Нажмите Ctrl+C для остановки.")

    application.run_polling()


if __name__ == "__main__":
    main()
