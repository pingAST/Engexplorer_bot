import sqlalchemy
import json

# token бота @Engexplorer_bot
token = ""

# Подключение к базе данных PostgreSQL
DNS = 'postgresql://postgres:<password>@localhost:5432/<name_db>'
engine = sqlalchemy.create_engine(DNS)


# default JSON файла с данными категорий и слов
data = {
    "categories": [
        {"name_ct": "Страны", "general": True},
        {"name_ct": "Средства передвижения", "general": True},
        {"name_ct": "Фрукты", "general": True},
        {"name_ct": "Животные", "general": True},
        {"name_ct": "Профессии", "general": True}
    ],
    "words": [
        {"name_word": "Россия", "category_id": 1, "general": True},
        {"name_word": "Франция", "category_id": 1, "general": True},
        {"name_word": "Япония", "category_id": 1, "general": True},
        {"name_word": "Бразилия", "category_id": 1, "general": True},
        {"name_word": "Италия", "category_id": 1, "general": True},
        {"name_word": "Германия", "category_id": 1, "general": True},
        {"name_word": "Китай", "category_id": 1, "general": True},
        {"name_word": "Испания", "category_id": 1, "general": True},
        {"name_word": "Турция", "category_id": 1, "general": True},
        {"name_word": "Канада", "category_id": 1, "general": True},

        {"name_word": "Машина", "category_id": 2, "general": True},
        {"name_word": "Велосипед", "category_id": 2, "general": True},
        {"name_word": "Поезд", "category_id": 2, "general": True},
        {"name_word": "Самолет", "category_id": 2, "general": True},
        {"name_word": "Корабль", "category_id": 2, "general": True},
        {"name_word": "Мотоцикл", "category_id": 2, "general": True},
        {"name_word": "Автобус", "category_id": 2, "general": True},
        {"name_word": "Трамвай", "category_id": 2, "general": True},
        {"name_word": "Метро", "category_id": 2, "general": True},
        {"name_word": "Яхта", "category_id": 2, "general": True},

        {"name_word": "Яблоко", "category_id": 3, "general": True},
        {"name_word": "Банан", "category_id": 3, "general": True},
        {"name_word": "Апельсин", "category_id": 3, "general": True},
        {"name_word": "Клубника", "category_id": 3, "general": True},
        {"name_word": "Ананас", "category_id": 3, "general": True},
        {"name_word": "Груша", "category_id": 3, "general": True},
        {"name_word": "Виноград", "category_id": 3, "general": True},
        {"name_word": "Мандарин", "category_id": 3, "general": True},
        {"name_word": "Лимон", "category_id": 3, "general": True},
        {"name_word": "Киви", "category_id": 3, "general": True},

        {"name_word": "Собака", "category_id": 4, "general": True},
        {"name_word": "Кошка", "category_id": 4, "general": True},
        {"name_word": "Лев", "category_id": 4, "general": True},
        {"name_word": "Тигр", "category_id": 4, "general": True},
        {"name_word": "Зебра", "category_id": 4, "general": True},
        {"name_word": "Слон", "category_id": 4, "general": True},
        {"name_word": "Обезьяна", "category_id": 4, "general": True},
        {"name_word": "Попугай", "category_id": 4, "general": True},
        {"name_word": "Лиса", "category_id": 4, "general": True},
        {"name_word": "Медведь", "category_id": 4, "general": True},

        {"name_word": "Врач", "category_id": 5, "general": True},
        {"name_word": "Учитель", "category_id": 5, "general": True},
        {"name_word": "Инженер", "category_id": 5, "general": True},
        {"name_word": "Повар", "category_id": 5, "general": True},
        {"name_word": "Актер", "category_id": 5, "general": True},
        {"name_word": "Пожарник", "category_id": 5, "general": True},
        {"name_word": "Певец", "category_id": 5, "general": True},
        {"name_word": "Полицейский", "category_id": 5, "general": True},
        {"name_word": "Дизайнер", "category_id": 5, "general": True},
        {"name_word": "Спортсмен", "category_id": 5, "general": True},

    ]
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
