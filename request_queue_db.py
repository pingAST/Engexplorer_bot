import json
from conf import engine
from modelDB import Word, create_tables, UserWord, User, UserCategory, Category
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()


def add_word_to_category(word_name, category_id, user_id):
    word = session.query(Word).filter(Word.name_word == word_name, Word.category_id == category_id).first()

    if word:
        user_word = session.query(UserWord).filter(UserWord.user_id == user_id, UserWord.word_id == word.id).first()
        if user_word and not user_word.flag_active:
            user_word.flag_active = True
            session.commit()
            return True

    word = Word(name_word=word_name, category_id=category_id, general=False)
    session.add(word)
    session.commit()

    user_word = UserWord(user_id=user_id, word_id=word.id, flag_active=True)
    session.add(user_word)
    session.commit()

    return True


def remove_word_from_category(word_name, category_id):
    word = session.query(Word).filter(Word.name_word == word_name, Word.category_id == category_id).first()
    if word:
        session.delete(word)
        session.commit()
        return True
    return False


def get_random_word_from_category(telegram_id, category_id):
    user = session.query(User).filter_by(id_telega=telegram_id).first()
    if user:
        # Получаем все категории пользователя
        user_categories = session.query(UserCategory).filter_by(user_id=user.id).all()
        print(user_categories)
        if user_categories:
            # Проверяем, есть ли у пользователя доступ к данной категории
            user_category_ids = [uc.category_id for uc in user_categories]
            if category_id not in user_category_ids:
                return None

            # Получаем случайное слово из указанной категории
            random_word = session.query(Word).filter_by(category_id=category_id, flag_active=True) \
                .order_by(func.random()).first()
            return random_word

    return None


def add_data_from_json_to_db():
    with open('./data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        # Проверяем, есть ли уже данные в таблице categories
        for category_data in data['categories']:
            existing_category = session.query(Category).filter_by(name_ct=category_data['name_ct']).first()
            if not existing_category:
                category = Category(name_ct=category_data['name_ct'],
                                    general=category_data['general'])
                session.add(category)
        # Проверяем, есть ли уже данные в таблице words
        for word_data in data['words']:
            existing_word = session.query(Word).filter_by(name_word=word_data['name_word']).first()
            if not existing_word:
                word = Word(name_word=word_data['name_word'], category_id=word_data['category_id'],
                            general=word_data['general'])
                session.add(word)

    session.commit()


def get_userid(user_id):
    user = session.query(User).filter_by(id_telega=user_id).first()
    return user


def add_user_in_tables(message, user_id):
    new_user = User(id_telega=user_id, nickname=message.from_user.first_name, username=message.from_user.username,
                    subs=True)
    session.add(new_user)
    session.commit()

    categories = session.query(Category).filter(Category.general == True).all()
    words = session.query(Word).filter(Word.general == True).all()

    for category in categories:
        user_category = UserCategory(user_id=new_user.id, category_id=category.id, flag_active=True)
        session.add(user_category)

    for word in words:
        user_word = UserWord(user_id=new_user.id, word_id=word.id,
                             flag_active=True)
        session.add(user_word)

    session.commit()


def get_categories(user_id):
    user_categories = session.query(UserCategory).filter(UserCategory.user_id == user_id, UserCategory.flag_active == True).all()
    category_ids = [uc.category_id for uc in user_categories]
    categories = session.query(Category).filter(Category.id.in_(category_ids)).all()

    return categories


def add_categories(user_id, add_category):
    existing_category = session.query(Category).filter_by(name_ct=add_category).first()

    if existing_category:
        user_category = session.query(UserCategory).filter_by(user_id=user_id, category_id=existing_category.id).first()
        if user_category and not user_category.flag_active:
            user_category.flag_active = True
            session.commit()
            return

    new_category = Category(name_ct=add_category, general=False)
    session.add(new_category)
    session.commit()

    user_category = UserCategory(user_id=user_id, category_id=new_category.id, flag_active=True)
    session.add(user_category)
    session.commit()


def delete_category(user_id, category_id):
    session.query(UserCategory).filter_by(user_id=user_id, category_id=category_id).update({'flag_active': False})
    session.commit()


def delete_word_from_category(word_id, category_id, user_id):
    word = session.query(Word).filter(Word.id == word_id,
                                      Word.category_id == category_id).first()

    if word:
        user_word = session.query(UserWord).filter(UserWord.user_id == user_id, UserWord.word_id == word.id).first()
        if user_word:
            user_word.flag_active = False
            session.commit()
            return True

    return False


def delete_all_words_in_category(user_id, category_id):
    user_words = session.query(UserWord).join(Word).filter(Word.category_id == category_id, UserWord.user_id == user_id, UserWord.flag_active == True).all()

    for user_word in user_words:
        user_word.flag_active = False

    session.commit()

    return True


def get_id_categories(category_id):
    id_categories = session.query(Category).filter_by(id=category_id).first()
    return id_categories


def get_word_by_id(word_id):
    word = session.query(Word).filter(Word.id == word_id).first()
    return word.name_word


def get_category_name(category_id):
    category = session.query(Category).filter_by(id=category_id).first()
    return category.name_ct


def get_words_in_category(category_id, user_id):
    user_category = session.query(UserCategory).filter(UserCategory.user_id == user_id, UserCategory.category_id == category_id, UserCategory.flag_active == True).first()

    if user_category:
        # Получаем слова из указанной категории, которые доступны пользователю
        user_words = session.query(Word).join(UserWord).filter(Word.category_id == category_id, UserWord.user_id == user_id, UserWord.flag_active == True).all()
        return user_words
