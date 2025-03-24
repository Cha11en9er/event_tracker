from datetime import datetime
import pytz
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import psycopg2, psycopg2.extras
import os

load_dotenv()

def db_connection():
    env_host = os.getenv('DB_HOST')
    env_port = os.getenv('DB_PORT')
    env_database = os.getenv('DB_NAME')
    env_user = os.getenv('DB_USER')
    env_password = os.getenv('DB_PASSWORD')
    connection = psycopg2.connect(host=env_host, port=env_port, database=env_database, user=env_user, password=env_password) 
    return connection

def get_notif_data():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
                    SELECT json_agg(n)
                    FROM (
                        SELECT
                            notification_id,
                            user_id,
                            user_telegram_id,
                            event_date,
                            notif_user_time,
                            notif_time,
                            notif_status,
                            event_name
                        FROM evt.notification
                    ) n;
                  """)
    rows = cursor.fetchone()[0]
    connection.commit() 
    cursor.close() 
    connection.close()
    
    return rows


moscow_tz = pytz.timezone('Europe/Moscow')

moscow_time = datetime.now(moscow_tz)

get_notif_data()

for i in get_notif_data():
    datetime_event_time = datetime.fromisoformat(i['event_date'])
    datetime_moscow_now = moscow_tz.localize(datetime_event_time)
    if datetime_event_time > moscow_time:
        print(datetime_event_time, moscow_time)

TOKEN =  os.getenv('TG_BOT_TOKEN')







# CHAT_ID = ''

# # Время, когда нужно отправить сообщение (в формате Unix timestamp)
# TARGET_TIME = 1700524800  # Пример: 2023-11-20 12:00:00 UTC

# # Создайте экземпляр бота
# bot = Bot(token=TOKEN)

# # Функция для отправки сообщения
# def send_message():
#     try:
#         bot.send_message(chat_id=CHAT_ID, text="Это оповещение!")
#         print("Сообщение отправлено.")
#     except TelegramError as e:
#         print(f"Ошибка при отправке сообщения: {e}")

# # Ожидание до нужного времени
# current_time = time.time()
# time_to_wait = TARGET_TIME - current_time

# if time_to_wait > 0:
#     print(f"Ожидание {time_to_wait} секунд перед отправкой сообщения.")
#     time.sleep(time_to_wait)

# # Отправка сообщения
# send_message()
