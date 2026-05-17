import sqlite3
import os
import json
import requests

# Получаем переменную из окружения
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
DB_URL = os.environ.get("DB_URL", "https://glamping-bot.website.yandexcloud.net/glamping.db")
DB_NAME = '/tmp/glamping.db'

# Состояния для отслеживания шагов пользователя
user_states = {}


def handler(event, context):
    # Точка входа для Cloud Function
    try:
        # Получаем данные из запроса от Telegram
        body = event.get('body', '{}')
        if isinstance(body, str):
            update = json.loads(body)
        else:
            update = body
        
        # Проверяем, есть ли сообщение
        if 'message' not in update:
            return {
                'statusCode': 200,
                'body': 'OK'
            }
        
        message = update['message']
        
        # Проверяем, есть ли текст в сообщении
        if 'text' not in message:
            return {
                'statusCode': 200,
                'body': 'OK'
            }
        
        chat_id = message['chat']['id']
        text = message['text']
        
        # Проверяем команду /start
        if text == '/start':
            process_start(chat_id)
            return {
                'statusCode': 200,
                'body': 'OK'
            }
        
        # Проверяем кнопку "Начать заново"
        if text == 'Начать заново':
            process_start(chat_id)
            return {
                'statusCode': 200,
                'body': 'OK'
            }
        
        # Проверяем, есть ли активное состояние у пользователя
        if chat_id not in user_states:
            send_message(chat_id, "Напишите /start чтобы начать поиск глэмпинга.")
            return {
                'statusCode': 200,
                'body': 'OK'
            }
        
        state = user_states[chat_id]['state']
        
        # Обрабатываем сообщение в зависимости от текущего состояния
        if state == 'DISTANCE':
            process_distance(chat_id, text)
        elif state == 'CAPACITY':
            process_capacity(chat_id, text)
        elif state == 'PURPOSE':
            process_purpose(chat_id, text)
        elif state == 'BUDGET':
            process_budget(chat_id, text)
        
        return {
            'statusCode': 200,
            'body': 'OK'
        }
        
    except Exception as e:
        print(f"Ошибка в handler: {e}")
        return {
            'statusCode': 500,
            'body': 'Error'
        }


def process_start(chat_id):
    # Обрабатывает команду /start
    reset_user_state(chat_id)
    user_states[chat_id] = {'state': 'DISTANCE', 'data': {}}
    
    text = "Привет! Я помогу подобрать глэмпинг недалеко от Екатеринбурга.\n\nНа каком расстоянии от города искать?"
    keyboard = build_keyboard([
        ["до 30 км", "30-60 км"],
        ["60-100 км", "100-150 км"]
    ])
    send_message(chat_id, text, keyboard)


def process_distance(chat_id, text):
    # Обрабатывает выбор расстояния
    valid_distances = ["до 30 км", "30-60 км", "60-100 км", "100-150 км"]
    
    if text not in valid_distances:
        send_message(chat_id, "Пожалуйста, выберите расстояние из предложенных вариантов.")
        return
    
    user_states[chat_id]['data']['distance'] = text
    user_states[chat_id]['state'] = 'CAPACITY'
    
    send_message(
        chat_id,
        "Сколько человек необходимо разместить?\nВведите целое число:",
        {'remove_keyboard': True}
    )


def process_capacity(chat_id, text):
    # Обрабатывает ввод количества человек
    try:
        capacity = int(text)
        if capacity <= 0:
            raise ValueError
    except ValueError:
        send_message(chat_id, "Пожалуйста, введите целое положительное число.")
        return
    
    user_states[chat_id]['data']['capacity'] = capacity
    user_states[chat_id]['state'] = 'PURPOSE'
    
    keyboard = build_keyboard([
        ["романтический", "шумная тусовка"],
        ["семейный"]
    ])
    send_message(chat_id, "Какой тип отдыха вас интересует?", keyboard)


def process_purpose(chat_id, text):
    # Обрабатывает выбор типа отдыха
    valid_purposes = ["романтический", "шумная тусовка", "семейный"]
    
    if text not in valid_purposes:
        send_message(chat_id, "Пожалуйста, выберите тип отдыха из предложенных вариантов.")
        return
    
    user_states[chat_id]['data']['purpose'] = text
    user_states[chat_id]['state'] = 'BUDGET'
    
    keyboard = build_keyboard([
        ["до 5000 руб", "5000-10000 руб"],
        ["10000-20000 руб", "от 20000 руб"]
    ])
    send_message(chat_id, "Какой бюджет на компанию за ночь?", keyboard)


def process_budget(chat_id, text):
    # Обрабатывает выбор бюджета и показывает результаты
    valid_budgets = ["до 5000 руб", "5000-10000 руб", "10000-20000 руб", "от 20000 руб"]
    
    if text not in valid_budgets:
        send_message(chat_id, "Пожалуйста, выберите бюджет из предложенных вариантов.")
        return
    
    user_states[chat_id]['data']['budget'] = text
    data = user_states[chat_id]['data']
    
    # Выполняем поиск
    try:
        results = search_glampings(
            data['distance'],
            data['capacity'],
            data['purpose'],
            data['budget']
        )
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        send_message(chat_id, "Произошла ошибка при поиске. Попробуйте позже.")
        reset_user_state(chat_id)
        return
    
    reset_user_state(chat_id)
    keyboard = build_keyboard([["Начать заново"]], one_time=False)
    
    if not results:
        send_message(chat_id, "Ничего не нашлось, попробуй другие параметры.", keyboard)
    else:
        for row in results:
            send_message(chat_id, format_glamping(row))
        
        send_message(chat_id, "Это все подходящие варианты!", keyboard)


def download_database():
    # Скачивает базу данных из публичного бакета, если её нет локально
    if os.path.exists(DB_NAME):
        return
    
    try:
        print(f"Скачиваю базу данных из {DB_URL}...")
        response = requests.get(DB_URL, timeout=30)
        
        if response.status_code == 200:
            with open(DB_NAME, 'wb') as f:
                f.write(response.content)
            print(f"База данных успешно загружена (размер: {len(response.content)} байт)")
        else:
            raise Exception(f"Сервер вернул статус {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети при загрузке базы данных: {e}")
        raise
    except Exception as e:
        print(f"Ошибка при загрузке базы данных: {e}")
        raise


def get_db_connection():
    # Создает подключение к базе данных с предварительной загрузкой
    download_database()
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def search_glampings(distance_range, capacity, purpose, budget_range):
    # Ищет глэмпинги по заданным параметрам.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Определяем диапазон расстояний
    if distance_range == "до 30 км":
        min_dist, max_dist = 0, 30
    elif distance_range == "30-60 км":
        min_dist, max_dist = 30, 60
    elif distance_range == "60-100 км":
        min_dist, max_dist = 60, 100
    elif distance_range == "100-150 км":
        min_dist, max_dist = 100, 150
    else:
        conn.close()
        return []
    
    # Маппинг типов отдыха
    purpose_map = {
        "романтический": "romantic",
        "шумная тусовка": "shady_party",
        "семейный": "family"
    }
    purpose_db = purpose_map.get(purpose)
    if not purpose_db:
        conn.close()
        return []
    
    # Определяем диапазон бюджета
    if budget_range == "до 5000 руб":
        min_price, max_price = 0, 5000
    elif budget_range == "5000-10000 руб":
        min_price, max_price = 5000, 10000
    elif budget_range == "10000-20000 руб":
        min_price, max_price = 10000, 20000
    elif budget_range == "от 20000 руб":
        min_price, max_price = 20000, 999999999
    else:
        conn.close()
        return []
    
    cursor.execute('''
        SELECT * FROM glampings
        WHERE distance_km > ? AND distance_km <= ?
        AND capacity >= ?
        AND purpose = ?
        AND price_per_night >= ? AND price_per_night <= ?
        ORDER BY distance_km, price_per_night
    ''', (min_dist, max_dist, capacity, purpose_db, min_price, max_price))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def get_amenities_text(row):
    # Собирает строку с удобствами
    amenities = []
    if row['has_banya']:
        amenities.append("есть баня")
    if row['has_chan']:
        amenities.append("есть чан")
    if row['has_terrace']:
        amenities.append("есть терраса")
    
    text = ", ".join(amenities).capitalize() if amenities else ""
    
    if row['notes']:
        if text:
            text += "\n" + row['notes']
        else:
            text = row['notes']
    
    return text


def format_glamping(row):
    # Форматирует один вариант глэмпинга для вывода
    amenities = get_amenities_text(row)
    
    message = (
        f"🏕 {row['glamping_name']}\n"
        f"🔗 Ссылка: {row['booking_link']}\n"
    )
    
    if amenities:
        message += f"📝 {amenities}\n"
    
    message += f"💰 Цена: {row['price_per_night']} руб. за домик (вмещает {row['capacity']} человек)"
    
    return message


def send_message(chat_id, text, reply_markup=None):
    # Отправка сообщения через Telegram Bot API
    if not TELEGRAM_TOKEN:
        print("Ошибка: TELEGRAM_TOKEN не установлен")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Ошибка отправки сообщения: {response.text}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


def build_keyboard(buttons, one_time=True):
    # Создает клавиатуру для ответа.
    keyboard = []
    for row in buttons:
        keyboard.append([{'text': btn} for btn in row])
    return {
        'keyboard': keyboard,
        'resize_keyboard': True,
        'one_time_keyboard': one_time
    }


def reset_user_state(chat_id):
    # Сбрасывает состояние пользователя
    if chat_id in user_states:
        del user_states[chat_id]