import sqlite3

DB_NAME = 'glamping.db'


def create_database():
    # Создание базы данных с глэмпингами
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS glampings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            glamping_name TEXT NOT NULL,
            distance_km INTEGER NOT NULL CHECK (distance_km > 0),
            purpose TEXT NOT NULL CHECK (purpose IN ('family', 'romantic', 'shady_party')),
            capacity INTEGER NOT NULL CHECK (capacity > 0),
            price_per_night INTEGER NOT NULL CHECK (price_per_night > 0),
            booking_link TEXT NOT NULL,
            notes TEXT DEFAULT '',
            has_banya INTEGER DEFAULT 0 CHECK (has_banya IN (0, 1)),
            has_chan INTEGER DEFAULT 0 CHECK (has_chan IN (0, 1)),
            has_terrace INTEGER DEFAULT 0 CHECK (has_terrace IN (0, 1))
        )
    ''')

    glampings = [
        ("ТК Энергетик", 25, "family", 2, 4200, "https://energy-base.ru/", "Есть открытый и закрытый бассейны, чан уже включен в стоимость", 0, 1, 0),
        ("ТК Энергетик", 25, "family", 4, 6800, "https://energy-base.ru/", "Есть открытый и закрытый бассейны, чан уже включен в стоимость", 1, 1, 0),
        ("ТК Энергетик", 25, "shady_party", 6, 11000, "https://energy-base.ru/", "Есть открытый и закрытый бассейны, чан уже включен в стоимость", 1, 0, 1),
        ("ЁлкиПалки", 35, "family", 4, 7500, "https://vk.ru/elkipalki_ekb", "Есть детская площадка, предоставляется детский стульчик и манеж, включен завтрак", 1, 0, 0),
        ("ЁлкиПалки", 35, "romantic", 2, 7000, "https://vk.ru/elkipalki_ekb", "Есть детская площадка, предоставляется детский стульчик и манеж, включен завтрак", 0, 0, 1),
        ("Глемпинг На Чусовой", 55, "family", 4, 8000, "https://nachusovoi.ru/", "Можно заказать завтрак, есть детская площадка", 1, 1, 1),
        ("Глемпинг На Чусовой", 55, "romantic", 2, 5900, "https://nachusovoi.ru/", "Можно заказать завтрак, есть детская площадка", 0, 1, 0),
        ("База ДухЛес", 57, "shady_party", 6, 12500, "https://bazaduhles.org.biz/", "", 1, 1, 1),
        ("База ДухЛес", 57, "family", 4, 7500, "https://bazaduhles.org.biz/", "", 1, 0, 0),
        ("База Светофор", 59, "shady_party", 8, 28000, "https://svetofor-base.ru/", "Скидка 25% на День рождения, есть детская площадка", 1, 1, 1),
        ("База Светофор", 59, "family", 4, 12000, "https://svetofor-base.ru/", "Скидка 25% на День рождения, есть детская площадка", 1, 0, 0),
        ("Дубровские просторы", 40, "romantic", 2, 5000, "https://dubrovskyprostory.ru/", "", 1, 1, 0),
        ("Дубровские просторы", 40, "family", 4, 7000, "https://dubrovskyprostory.ru/", "", 1, 1, 0),
        ("Gagarka village", 51, "shady_party", 6, 18000, "https://gagarka96.ru/", "Есть детская площадка, есть фурако (горячая купель на свежем воздухе)", 1, 1, 0),
        ("Gagarka village", 51, "romantic", 2, 11000, "https://gagarka96.ru/", "Есть детская площадка, есть фурако (горячая купель на свежем воздухе)", 1, 1, 1),
        ("Мариинские избы", 73, "shady_party", 10, 190500, "https://mariinskie-izbi.com/", "Проводятся экскурсии и мастер-классы", 1, 0, 1),
        ("Мариинские избы", 73, "family", 4, 18000, "https://mariinskie-izbi.com/", "Проводятся экскурсии и мастер-классы", 1, 1, 0),
        ("Lipkiglamp", 146, "romantic", 2, 9500, "https://lipkiglamp.ru/", "", 0, 1, 1),
        ("Lipkiglamp", 146, "family", 4, 14500, "https://lipkiglamp.ru/", "", 1, 0, 0),
        ("Загородный клуб Пески", 7, "shady_party", 6, 9700, "https://peski13.ru/", "При бронировании тир предоставляется бесплатно", 1, 0, 0),
        ("Загородный клуб Пески", 7, "family", 4, 6107, "https://peski13.ru/", "При бронировании тир предоставляется бесплатно", 0, 1, 0),
        ("Баден-Баден Сысерть", 50, "family", 2, 10500, "https://baden-sysert.ru/", "Есть большой банный комплекс с открытым бассейном", 1, 1, 1),
        ("Баден-Баден Сысерть", 50, "shady_party", 4, 13000, "https://baden-sysert.ru/", "Есть большой банный комплекс с открытым бассейном", 1, 0, 0),
        ("Белая лошадь", 40, "romantic", 2, 15000, "https://www.whorse.ru/", "Завтрак включен, есть спа, рестораны", 1, 1, 1),
        ("Белая лошадь", 40, "family", 4, 22000, "https://www.whorse.ru/", "Завтрак включен, есть спа, рестораны", 1, 0, 0),
        ("Термальный комплекс ЮГА", 20, "family", 4, 35000, "https://xn--80af4f.xn--p1ai/", "Термы включены, есть рестораны и бары", 1, 1, 1),
        ("Термальный комплекс ЮГА", 20, "shady_party", 6, 55000, "https://xn--80af4f.xn--p1ai/", "Термы включены, есть рестораны и бары", 1, 1, 0),
        ("Глемпинг Гостилья", 50, "shady_party", 6, 6900, "https://www.avito.ru/", "Есть аренда квадроцикла, обучение катанию", 1, 0, 0),
        ("Глемпинг Гостилья", 50, "romantic", 2, 4000, "https://www.avito.ru/", "Есть аренда квадроцикла, обучение катанию", 1, 0, 0),
        ("Барнхаус_96", 37, "shady_party", 8, 23000, "https://www.avito.ru/", "", 1, 1, 1),
        ("Барнхаус_96", 37, "family", 4, 12000, "https://www.avito.ru/", "", 1, 1, 0),
        ("Дом Бобра", 40, "shady_party", 6, 25000, "https://www.avito.ru/", "Есть свой летний бассейн", 1, 1, 1),
        ("Дом Бобра", 40, "family", 4, 15000, "https://www.avito.ru/", "Есть свой летний бассейн", 1, 1, 0),
        ("Сердце природы", 37, "romantic", 2, 6990, "https://сердце-природы.рф/", "", 1, 0, 1),
        ("Сердце природы", 37, "family", 4, 8990, "https://сердце-природы.рф/", "", 1, 0, 1),
        ("VinderVillage", 20, "romantic", 2, 3500, "https://vindervillage.ru/", "Есть летний бассейн", 0, 0, 1),
        ("VinderVillage", 20, "family", 4, 7000, "https://vindervillage.ru/", "Есть летний бассейн", 0, 0, 1),
        ("Хижина в лесу", 45, "romantic", 2, 4500, "https://hizhina-les.ru", "", 0, 0, 1),
        ("Хижина в лесу", 45, "family", 4, 7000, "https://hizhina-les.ru", "", 0, 1, 0),
        ("TeleCamp", 55, "shady_party", 8, 7600, "https://telecamp.ru/", "Есть мини SPA, круглогодичная купель, можно арендовать сап-борд, лодку", 1, 1, 1),
        ("TeleCamp", 55, "romantic", 2, 5600, "https://telecamp.ru/", "Есть мини SPA, круглогодичная купель, можно арендовать сап-борд, лодку", 0, 1, 1),
        ("Дивий камень", 100, "family", 4, 4000, "https://divykamen.ru", "Размещение в домиках или сафари-тентах, можно записаться на пленэр", 0, 0, 1),
        ("Дивий камень", 100, "romantic", 2, 3000, "https://divykamen.ru", "Размещение в домиках или сафари-тентах, можно записаться на пленэр", 0, 0, 1),
        ("Галактика", 25, "romantic", 2, 6900, "https://галактикалеса.рф/", "Размещение в геокуполе", 0, 1, 1),
        ("Суеты нет", 50, "shady_party", 6, 10000, "https://sueti.net/", "Домик на сваях. Есть детская площадка, спуск к воде", 1, 1, 1),
        ("Суеты нет", 50, "family", 4, 7000, "https://sueti.net/", "Домик на сваях. Есть детская площадка, спуск к воде", 1, 0, 0),
        ("Красивое место", 127, "romantic", 2, 5900, "https://krasivoye-mesto.ru/", "Главное достояние этого глэмпинга - расположение в природном парке Оленьи ручьи", 0, 0, 1),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO glampings 
        (glamping_name, distance_km, purpose, capacity, price_per_night, booking_link, notes, has_banya, has_chan, has_terrace)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', glampings)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_database()
    print("База данных успешно создана!")