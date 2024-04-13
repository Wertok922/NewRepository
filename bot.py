import telebot
from telebot import types

# Создаем объект бота с указанием вашего токена
bot = telebot.TeleBot("7054021076:AAFOMTwyVhYQETse8EMwSM24grMCX9uTwo4")

# Словарь для хранения баллов ЕГЭ пользователя и соответствующих специальностей
user_scores = {}
user_preferences = {}

# Словарь с проходными баллами для каждой специальности
passing_scores = {
    "Информационные технологии": {"subjects": ["Математика", "Русский язык"], "total_score": 140},
    "Филология": {"subjects": ["Русский язык", "Иностранный язык"], "total_score": 125},
    "Журналистика": {"subjects": ["Русский язык", "Иностранный язык"], "total_score": 125},
    "Лингвистика": {"subjects": ["Иностранный язык", "Русский язык"], "total_score": 125},
    "Международные отношения": {"subjects": ["Иностранный язык", "Русский язык"], "total_score": 125}
    # Добавьте еще специальности и соответствующие обязательные предметы и суммарные баллы
}

# Минимальные баллы за каждый предмет
min_scores = {"Математика": 40, "Русский язык": 40, "Иностранный язык": 40}

# Словарь с профессиями и интересами к ним
professions_interests = {
    "Информационные технологии": ["технология", "информация"],
    "Филология": ["филология", "литература"],
    "Журналистика": ["журналистика", "публицистика"],
    "Лингвистика": ["лингвистика", "перевод"],
    "Международные отношения": ["международные отношения", "дипломатия"]
    # Добавьте еще профессии и соответствующие им интересы
}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     "Привет! Я чат-бот, который поможет тебе определиться с выбором направления при поступлении в институт. Пожалуйста, введи команду /input для ввода своих баллов за ЕГЭ.")


# Обработчик команды /input
@bot.message_handler(commands=['input'])
def input_scores(message):
    bot.send_message(message.chat.id, "Выберите предметы ЕГЭ из списка ниже или команду /next, чтобы перейти дальше:",
                     reply_markup=generate_subjects_keyboard())


# Функция для генерации клавиатуры с предметами ЕГЭ
def generate_subjects_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    subjects = ["Математика", "Русский язык", "Иностранный язык"]
    keyboard.add(*[types.KeyboardButton(subject) for subject in subjects])
    return keyboard


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: message.text in ["Математика", "Русский язык", "Иностранный язык"])
def handle_subjects(message):
    user_scores[message.text] = None
    bot.send_message(message.chat.id, f"Введите балл за предмет '{message.text}':")


# Обработчик текстовых сообщений с баллами ЕГЭ
@bot.message_handler(func=lambda message: message.text.isdigit() or message.text.lower() == "/next")
def handle_scores(message):
    if message.text.isdigit():
        # Находим предмет, для которого пользователь вводит баллы
        subject = next(key for key in user_scores if user_scores[key] is None)
        score = int(message.text)

        if score < 40:
            bot.send_message(message.chat.id, "Вы уверены? Эти баллы являются слишком низкими. Вы не сдали экзамен.")
            return input_scores(message)  # Перезапуск ввода
        elif score > 100:
            bot.send_message(message.chat.id, "Ого, да ты машина, одумайся, ВУЗ не для тебя.")
            return input_scores(message)  # Перезапуск ввода
        else:
            user_scores[subject] = score
            bot.send_message(message.chat.id, f"Баллы за предмет '{subject}' успешно сохранены: {score}")
            return input_scores(message)
    elif message.text.lower() == "/next":
        # Создаем кастомную клавиатуру с интересами пользователя и кнопкой "Дальше"
        keyboard = generate_interests_keyboard()
        bot.send_message(message.chat.id,
                         "Теперь укажите ваши предпочтения (интересы, любимый предмет, область знаний и т.д.):",
                         reply_markup=keyboard)



# Функция для генерации клавиатуры с интересами пользователя и кнопкой "Дальше"
def generate_interests_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    interests = ["Технология", "Информация", "Литература", "Публицистика", "Перевод", "Дипломатия"]
    # Добавляем каждый интерес в качестве отдельной кнопки
    for interest in interests:
        keyboard.add(types.KeyboardButton(interest))
    # Добавляем кнопку "Дальше"
    keyboard.add(types.KeyboardButton("Дальше"))
    return keyboard


# Обработчик текстовых сообщений с пожеланиями пользователя
@bot.message_handler(
    func=lambda message: message.text in ["Технология", "Информация", "Литература", "Публицистика", "Перевод",
                                          "Дипломатия"])
def handle_interests(message):
    # Сохраняем выбранный интерес
    if message.chat.id not in user_preferences:
        user_preferences[message.chat.id] = []
    user_preferences[message.chat.id].append(message.text)
    bot.send_message(message.chat.id, f"Интерес '{message.text}' успешно сохранен.")
    # Предлагаем выбрать ещё один интерес или перейти дальше
    keyboard = generate_interests_keyboard()
    bot.send_message(message.chat.id, "Выберите ещё один интерес или нажмите 'Дальше':", reply_markup=keyboard)


# Обработчик нажатия на кнопку "Дальше"
@bot.message_handler(func=lambda message: message.text == "Дальше")
def handle_next(message):
    # Проверяем, что пользователь ввел баллы за основные предметы
    if "Математика" not in user_scores or "Русский язык" not in user_scores:
        bot.send_message(message.chat.id, "Пожалуйста, введите баллы за оба основных предмета перед нажатием кнопки 'Дальше'.")
        return

    # Если у пользователя есть предпочтения, вызываем соответствующий обработчик
    if message.chat.id in user_preferences:
        preferences = ", ".join(user_preferences[message.chat.id])  # Объединяем список в строку через запятую
        handle_preferences(message, preferences)
    else:
        bot.send_message(message.chat.id, "Вы ещё не выбрали ни одного интереса.")


# Функция для анализа предпочтений пользователя и вывода подходящих профессий
def find_matching_professions(preferences):
    matching_professions = []
    for profession, data in passing_scores.items():
        required_subjects = data["subjects"]
        total_score_required = data["total_score"]

        # Проверяем, что баллы по всем предметам из профессии не меньше требуемых
        total_score = sum(user_scores.get(subject, 0) for subject in required_subjects)
        passed_all_subjects = all(
            user_scores.get(subject) is not None and user_scores.get(subject) >= min_scores.get(subject, 40)
            for subject in required_subjects)

        if total_score >= total_score_required and passed_all_subjects:
            for interest in professions_interests[profession]:
                if interest.lower() in preferences.lower():
                    matching_professions.append(profession)
                    break
    return matching_professions




# Обработчик текстовых сообщений с предпочтениями пользователя
def handle_preferences(message, preferences):
    bot.send_message(message.chat.id, "Пожелания успешно сохранены!")

    # Находим подходящие профессии на основе предпочтений пользователя
    matching_professions = find_matching_professions(preferences)

    # Выводим подходящие профессии или сообщение о том, что профессии не найдены
    if matching_professions:
        bot.send_message(message.chat.id, "Подходящие профессии:")
        for profession in matching_professions:
            bot.send_message(message.chat.id, profession)
    else:
        bot.send_message(message.chat.id, "Подходящие профессии не найдены.")


# Запускаем бота
bot.polling()
