from datetime import datetime, timedelta
import pytz
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from dotenv import load_dotenv
import psycopg2, psycopg2.extras
import os
import asyncio
import time

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
                n.notification_id,
                n.user_id,
                n.user_telegram_id,
                n.event_date,
                n.notif_user_time,
                n.notif_time,
                n.notif_status,
                n.event_name
            FROM evt.notification n
            WHERE n.notif_status = 'Active'
            AND n.user_telegram_id IS NOT NULL
        ) n;
    """)
    
    result = cursor.fetchone()
    rows = result[0] if result and result[0] else []
    
    cursor.close() 
    connection.close()
    
    print("\n=== Полученные данные из БД ===")
    print(f"Всего активных уведомлений: {len(rows)}")
    for row in rows:
        print(f"\nУведомление ID: {row['notification_id']}")
        print(f"Событие: {row['event_name']}")
        print(f"Telegram ID: {row['user_telegram_id']}")
        print(f"Дата события: {row['event_date']}")
        print(f"Время уведомления (минут до события): {row['notif_user_time']}")
    print("==============================\n")
    
    return rows

async def send_notification(chat_id, event_name, event_time, notif_time):
    bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
    try:
        message = f"Напоминание! Событие '{event_name}' начнется менее чем через {notif_time} минут (в {event_time})"
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return False

def update_notification_status(notification_id):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE evt.notification 
            SET notif_status = 'Diactive' 
            WHERE notification_id = %s
        """, (notification_id,))
        connection.commit()
        print(f"Статус уведомления {notification_id} обновлен на 'Diactive'")
    except Exception as e:
        print(f"Ошибка при обновлении статуса уведомления: {e}")
    finally:
        cursor.close()
        connection.close()

async def check_notifications():
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_tz)
    print(f"\n=== Проверка уведомлений ===")
    print(f"Текущее время (МСК): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    notifications = get_notif_data()
    
    for notification in notifications:
        event_time = pytz.timezone('Europe/Moscow').localize(
            datetime.fromisoformat(str(notification['event_date']))
        )
        notif_time = event_time - timedelta(minutes=notification['notif_user_time'])
        
        print(f"\nПроверка уведомления {notification['notification_id']}:")
        print(f"Время события: {event_time}")
        print(f"Время уведомления: {notif_time}")
        
        # Если время события прошло
        if current_time > event_time:
            print(f"Событие уже прошло, меняем статус на Diactive")
            update_notification_status(notification['notification_id'])
            continue
        
        # Если текущее время в интервале между временем уведомления и временем события
        if notif_time <= current_time <= event_time:
            print(f"Отправляем уведомление")
            await send_notification(
                notification['user_telegram_id'],
                notification['event_name'],
                event_time.strftime('%H:%M'),
                notification['notif_user_time']
            )

async def send_feedback_request(chat_id, event_name):
    bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
    try:
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data=f"rate_1"),
                InlineKeyboardButton("2", callback_data=f"rate_2"),
                InlineKeyboardButton("3", callback_data=f"rate_3"),
                InlineKeyboardButton("4", callback_data=f"rate_4"),
                InlineKeyboardButton("5", callback_data=f"rate_5"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"Мероприятие '{event_name}' завершено. Пожалуйста, оцените его от 1 до 5:"
        await bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
        return True
    except TelegramError as e:
        print(f"Ошибка при отправке запроса на фидбек: {e}")
        return False

def get_finished_events():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT json_agg(e)
        FROM (
            SELECT 
                e.event_id,
                e.event_name,
                e.event_end_time,
                array_agg(ep.user_id) as participant_ids,
                array_agg(u.telegram_id) as telegram_ids
            FROM evt.event e
            JOIN evt.event_participation ep ON e.event_id = ep.event_id
            JOIN evt.user u ON ep.user_id = u.user_id
            WHERE e.event_end_time <= CURRENT_TIMESTAMP
            AND e.status = 'Active'
            GROUP BY e.event_id, e.event_name, e.event_end_time
        ) e;
    """)
    
    result = cursor.fetchone()
    events = result[0] if result and result[0] else []
    
    cursor.close()
    connection.close()
    return events

def update_event_status(event_id, status='Finished'):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE evt.event 
            SET status = %s 
            WHERE event_id = %s
        """, (status, event_id))
        connection.commit()
        print(f"Статус мероприятия {event_id} обновлен на '{status}'")
    except Exception as e:
        print(f"Ошибка при обновлении статуса мероприятия: {e}")
    finally:
        cursor.close()
        connection.close()

async def check_finished_events():
    print("\n=== Проверка завершенных мероприятий ===")
    events = get_finished_events()
    
    for event in events:
        print(f"\nОбработка мероприятия: {event['event_name']}")
        
        # Отправляем запрос на фидбек всем участникам
        for telegram_id in event['telegram_ids']:
            if telegram_id:
                await send_feedback_request(telegram_id, event['event_name'])
        
        # Обновляем статус мероприятия
        update_event_status(event['event_id'])

async def main():
    print("Запуск сервиса уведомлений...")
    while True:
        try:
            await check_notifications()
            await check_finished_events()  # Добавляем проверку завершенных мероприятий
            print("\nОжидание 15 минут до следующей проверки...")
            await asyncio.sleep(900)  # 15 минут
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(60)  # При ошибке ждем 1 минуту

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nЗавершение работы...")
