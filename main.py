import telebot
import random
import re
from telebot import types
from conf import token
from request_queue_db import add_data_from_json_to_db, get_userid, session, add_user_in_tables, get_categories, get_id_categories, get_words_in_category, get_word_by_id, delete_all_words_in_category, delete_category, get_category_name, add_categories, add_word_to_category, delete_word_from_category
from EngAPI import Translate

button_state = {}
used_words = []
current_word_index = 0

add_data_from_json_to_db()

bot = telebot.TeleBot(token)
translate = Translate()


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user = get_userid(user_id)
    if user:
        if not user.subs:
            user.subs = True
            session.commit()
        bot.reply_to(message, f"Привет, {user.nickname}👋!"
                              f" Вы успешно подписались на бота."
                              f"Выбери категорию слов, чтобы попрактиковаться в английском языке. Погнали!")
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        start_categories(message, user_id)
    else:
        bot.reply_to(message, f"Привет, {message.from_user.first_name}👋! Давай попрактикуемся в английском языке. "
                              f"Тренировки можешь проходить в удобном для себя темпе."
                              f"У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения.\n" 
                              f" Для этого воспользуйся инструментами:\n добавить слово ➕,\n удалить слово 🔙. \n Ну что, начнём ⬇️")
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        add_user_in_tables(message, user_id)
        start_categories(message, user_id)


def handle_subscribe(message, user_id):
    user = get_userid(user_id)
    if not user.subs:
        user.subs = True
        session.commit()
        bot.reply_to(message, f"Привет, {user.nickname}👋! Давай попрактикуемся в английском языке. "
                              f"Тренировки можешь проходить в удобном для себя темпе."
                              f"У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения.\n" 
                              f" Для этого воспользуйся инструментами:\n добавить слово ➕,\n удалить слово 🔙. \n Ну что, начнём ⬇️")
        start_categories(message, user_id)
    else:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(commands=['stop'])
def handle_stop(message, user_id=None):
    if not user_id:
        user_id = message.from_user.id
    user = get_userid(user_id)
    if user:
        user.subs = False
        session.commit()

        start_markup = types.InlineKeyboardMarkup(row_width=1)
        start_button = types.InlineKeyboardButton(text="✅Подписаться✅", callback_data="start_b")
        start_markup.add(start_button)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, "Вы успешно отписались от бота.", reply_markup=start_markup)


@bot.message_handler(commands=['categories'])
def start_categories(message, user_id):
    user = get_userid(user_id)
    if user:
        categories = get_categories(user.id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        for category in categories:
            button = types.InlineKeyboardButton(text=category.name_ct, callback_data=f"category_{category.id}")
            markup.add(button)

        # Создаем кнопку "Настройки"
        settings_button = types.InlineKeyboardButton(text="Настройки⚙️", callback_data="settings")
        markup.add(settings_button)

        bot.send_message(message.chat.id, f"Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Пользователь не найден")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.message.chat.id  # Получаем user_id из chat_id сообщения
    user = get_userid(user_id)
    if call.data.startswith('category_'):
        category_id = int(call.data.split('_')[1])
        category = get_id_categories(category_id)
        if category:
            words_in_category = get_words_in_category(category_id, user.id)
            if words_in_category:
                word_list = "\n".join([f"{i + 1}. {word.name_word}" for i, word in enumerate(words_in_category)])
                count = len(words_in_category)  # Устанавливаем значение счетчика как количество слов
                markup = create_buttons(category_id, count)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Слова в категории {category.name_ct} ({count} слов):\n{word_list}",
                                      reply_markup=markup)

            else:
                markup = create_buttons(category_id, count=0)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Слова в категории {category.name_ct} не найдены", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "Категория не найдена")

        bot.answer_callback_query(call.id)

    elif call.data.startswith('add_word_'):
        category_id = int(call.data.split('_')[-1])
        category = get_id_categories(category_id)
        user_id = call.message.chat.id
        user = get_userid(user_id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id,
                         f"Введите слово, которое хотите добавить в категорию {category.name_ct}:")
        bot.register_next_step_handler(call.message,
                                       lambda message: process_add_word(message, category_id, user.id, category))

    elif call.data.startswith('rm_word_'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        category_id = int(call.data.split('_')[-1])
        words = get_words_in_category(category_id, user.id)
        delete_markup = types.InlineKeyboardMarkup(row_width=1)

        for word in words:
            button = types.InlineKeyboardButton(text=f"❌{word.name_word}",
                                                callback_data=f"rm_word_bt_{word.id}_{category_id}")
            delete_markup.add(button)

        back_button = types.InlineKeyboardButton(text="К категориям🔙", callback_data="back_to_categories")
        delete_markup.add(back_button)

        bot.send_message(call.message.chat.id, "Выберите слово для удаления:", reply_markup=delete_markup)

        if call.data.startswith('rm_word_bt_'):
            data_parts = call.data.split('_')
            word_id = int(data_parts[3])
            category_id = int(data_parts[4])

            if delete_word_from_category(word_id, category_id, user.id):
                bot.send_message(call.message.chat.id, f"Слово успешно удалено из категории.")
                # Обновляем сообщение с новым списком слов в категории
                words_in_category = get_words_in_category(category_id, user.id)
                word_list = "\n".join([f"{i + 1}. {word.name_word}" for i, word in enumerate(words_in_category)])
                count = len(words_in_category)  # Устанавливаем значение счетчика как количество слов
                markup = create_buttons(category_id, count)
                bot.send_message(call.message.chat.id, f"Слова в категории ({count} слов):\n{word_list}",
                                 reply_markup=markup)
            else:
                bot.send_message(call.message.chat.id, f"Не удалось удалить слово из категории.")

    elif call.data.startswith('continue_learning_'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        category_id = int(call.data.split('_')[-1])
        category = get_id_categories(category_id)
        words_in_category = get_words_in_category(category_id, user.id)

        chosen_word = get_unique_word(words_in_category)
        translated_result = translate.show_text(chosen_word.name_word)
        ask_question(call, chosen_word, translated_result, words_in_category, category_id)


    elif call.data.startswith('check_answer_'):
        user_answer = call.data.split('_')[2]
        chosen_word = int(call.data.split('_')[3])
        category_id = int(call.data.split('_')[4])
        category = get_id_categories(category_id)
        words_in_category = get_words_in_category(category_id, user.id)
        word_to_check = get_word_by_id(chosen_word)

        if translate.check_answer(word_to_check, user_answer):
            bot.send_message(call.message.chat.id, text=f"Правильно💡! \n{word_to_check} -> {user_answer}")

            chosen_word = get_unique_word(words_in_category)
            translated_result = translate.show_text(chosen_word.name_word)

            ask_question(call, chosen_word, translated_result, words_in_category, category_id)

        else:
            bot.send_message(call.message.chat.id, text="Неправильно. Попробуйте снова.")

    elif call.data.startswith('delete_all_words_'):
        category_id = int(call.data.split('_')[-1])
        category = get_id_categories(category_id)
        success = delete_all_words_in_category(user.id, category_id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if success:
            bot.send_message(user_id, f"Все слова в категории успешно удалены")
            markup = create_buttons(category_id, count=0)
            bot.send_message(call.message.chat.id, f"Слова в категории {category.name_ct} не найдены",
                             reply_markup=markup)
        else:
            bot.send_message(user_id, f"Не удалось удалить все слова в категории")

    elif call.data == 'settings':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        settings_markup = create_settings_markup()
        bot.send_message(call.message.chat.id, f"Выберите действие:{txt_all_category(user)}",
                         reply_markup=settings_markup)

    elif call.data == 'back_to_categories':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start_categories(call.message, user_id)

    elif call.data == 'add_category':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Введите название категории:")
        button_state[call.message.chat.id] = 'add_category'

    elif call.data == 'delete_category':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        categories = get_categories(user.id)
        delete_markup = types.InlineKeyboardMarkup(row_width=1)
        for category in categories:
            button = types.InlineKeyboardButton(text=f"❌{category.name_ct}",
                                                callback_data=f"delete_{category.id}")
            delete_markup.add(button)

        back_button = types.InlineKeyboardButton(text="К категориям🔙", callback_data="back_to_categories")
        delete_markup.add(back_button)
        bot.send_message(call.message.chat.id, "Выберите категорию для удаления:", reply_markup=delete_markup)
        delete_category_button = types.InlineKeyboardButton(text="Удалить категорию❌", callback_data="delete_category")
        delete_markup.add(delete_category_button)

    elif call.data.startswith('delete_'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        category_id = int(call.data.split('_')[1])
        delete_category(user.id, category_id)
        category_name = get_category_name(category_id)
        bot.send_message(call.message.chat.id, f"Категория '{category_name}' успешно удалена!")
        settings_markup = create_settings_markup()
        bot.send_message(call.message.chat.id, f"Выберите действие:{txt_all_category(user)}",
                         reply_markup=settings_markup)

    elif call.data == 'stop_b':
        handle_stop(call.message, user_id)

    elif call.data == 'start_b':
        handle_subscribe(call.message, user_id)


def get_unique_word(words_in_category):
    unique_word = random.choice(words_in_category)
    while unique_word.id in used_words:
        unique_word = random.choice(words_in_category)
    used_words.append(unique_word.id)
    return unique_word


def continue_learning(chosen_word, translated_result, words_in_category):
    correct_answer = translated_result['destination_text']

    wrong_answers = [translate.show_text(word.name_word).get('destination_text') for word in words_in_category if
                     word != chosen_word]
    answers = [correct_answer] + random.sample(wrong_answers, 3)

    return answers


def ask_question(call, chosen_word, translated_result, words_in_category, category_id):
    answers = continue_learning(chosen_word, translated_result, words_in_category)
    random.shuffle(answers)
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for answer in answers:
        keyboard.add(types.InlineKeyboardButton(answer,
                                                callback_data=f'check_answer_{answer.lower()}_{chosen_word.id}_{category_id}'))

    keyboard.add(types.InlineKeyboardButton(text="К категориям🔙", callback_data="back_to_categories"))
    bot.send_message(call.message.chat.id,
                     text=f"Как переводится слово 🇷🇺 {translated_result['source_text']} на английский язык?",
                     reply_markup=keyboard)

    global current_word_index
    current_word_index += 1

    keyboard1 = types.InlineKeyboardMarkup(row_width=1)

    if current_word_index == len(words_in_category):
        keyboard1.add(types.InlineKeyboardButton(text="К категориям🔙", callback_data="back_to_categories"))
        bot.send_message(chat_id=call.message.chat.id, text="Вы прошли все слова в этой категории!", reply_markup=keyboard1)


def create_settings_markup():
    settings_markup = types.InlineKeyboardMarkup(row_width=2)
    add_category_button = types.InlineKeyboardButton(text="Добавить категорию➕", callback_data=f"add_category")
    settings_markup.add(add_category_button)
    delete_category_button = types.InlineKeyboardButton(text="Удалить категорию❌", callback_data=f"delete_category")
    settings_markup.add(delete_category_button)
    back_button = types.InlineKeyboardButton(text="К категориям🔙", callback_data="back_to_categories")
    settings_markup.add(back_button)
    stop_button = types.InlineKeyboardButton(text="Отписаться❌", callback_data="stop_b")
    settings_markup.add(stop_button)

    return settings_markup


def create_buttons(category_id, count):
    add_button = types.InlineKeyboardButton(text="Добавить слово➕", callback_data=f"add_word_{category_id}")
    remove_button = types.InlineKeyboardButton(text="Удалить слово❌", callback_data=f"rm_word_{category_id}")
    delete_all_words_button = types.InlineKeyboardButton(text="❌Удалить все слова в категории❌",
                                                         callback_data=f"delete_all_words_{category_id}")
    back_button = types.InlineKeyboardButton(text="К категориям🔙", callback_data="back_to_categories")

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(add_button, remove_button)
    markup.add(delete_all_words_button)
    if count >= 4:
        continue_button = types.InlineKeyboardButton(text="К изучению ➡",
                                                     callback_data=f"continue_learning_{category_id}")
        markup.add(continue_button)
    markup.add(back_button)

    return markup


@bot.message_handler(
    func=lambda message: message.chat.id in button_state and button_state[message.chat.id] == 'add_category')
def handle_new_category(message):
    user_id = message.from_user.id
    user = get_userid(user_id)

    add_category = message.text

    if not is_russian_word(add_category):
        bot.send_message(message.chat.id, "Пожалуйста, введите слово на русском языке.")
        settings_markup = create_settings_markup()
        bot.send_message(message.chat.id, f"Выберите действие:{txt_all_category(user)}", reply_markup=settings_markup)
        return

    if has_duplicate_word(get_categories(user.id), add_category):
        bot.send_message(message.chat.id, f"Категория '{add_category}' уже существует в категориях.")
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        settings_markup = create_settings_markup()
        bot.send_message(message.chat.id, f"Выберите действие:{txt_all_category(user)}", reply_markup=settings_markup)
        return

    add_categories(user.id, add_category)  # Вызываем функцию для добавления категории

    bot.send_message(message.chat.id, f"Категория '{add_category}' успешно добавлена!")
    del button_state[message.chat.id]  # Удаляем состояние кнопки
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    settings_markup = create_settings_markup()
    bot.send_message(message.chat.id, f"Выберите действие:{txt_all_category(user)}", reply_markup=settings_markup)


def txt_all_category(user):
    categories = get_categories(user.id)
    message_text = "\nВот список категорий:\n"
    count = 1
    for category in categories:
        message_text += f"{count}.{category.name_ct}\n"
        count += 1

    return message_text


def process_add_word(message, category_id, user_id, category):
    words = message.text.split(",")  # Разделяем введенную строку на отдельные слова по запятой
    for word in words:
        word = word.strip()
        if not is_russian_word(word):
            bot.send_message(message.chat.id, f"Слово '{word}' должно состоять только из русских букв")
            continue
        if is_word_unique(word, category_id, user_id):
            success = add_word_to_category(word.strip(), category_id, user_id)
            if success:
                bot.send_message(message.chat.id, f"Слово '{word.strip()}' успешно добавлено в категорию")

            else:
                bot.send_message(message.chat.id, "Что-то пошло не так при добавлении слова в категорию")
        else:
            bot.send_message(message.chat.id, f"Слово '{word}' уже существует в данной категории")

    words_in_category = get_words_in_category(category_id, user_id)
    word_list = "\n".join([f"{i + 1}. {word.name_word}" for i, word in enumerate(words_in_category)])
    count = len(words_in_category)  # Устанавливаем значение счетчика как количество слов
    markup = create_buttons(category_id, count)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.send_message(message.chat.id, f"Слова в категории {category.name_ct} ({count} слов):\n{word_list}",
                     reply_markup=markup)


def is_russian_word(word):
    return bool(re.match(r'^[А-ЯЁа-яё]', word))


def is_word_unique(word, category_id, user_id):
    existing_words = get_words_in_category(category_id, user_id)
    return all(existing_word.name_word.lower() != word.lower() for existing_word in existing_words)


def has_duplicate_word(words_list, new_word):
    return new_word.lower() in [word.name_ct.lower() for word in words_list]


# Запуск бота
bot.polling()
# Реализуйте функции для работы с API перевода слов

# Реализуйте функцию для напоминаний об изучении английского языка

# Запустите бот
bot.polling()
session.close()
