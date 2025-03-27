from datetime import datetime, timedelta
import pytz
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import psycopg2, psycopg2.extras
import os
import time
import asyncio
import signal

load_dotenv()

def db_connection():
    env_host = os.getenv('DB_HOST')
    env_port = os.getenv('DB_PORT')
    env_database = os.getenv('DB_NAME')
    env_user = os.getenv('DB_USER')
    env_password = os.getenv('DB_PASSWORD')
    print(f"\nПодключение к БД:")
    print(f"Host: {env_host}")
    print(f"Port: {env_port}")
    print(f"Database: {env_database}")
    print(f"User: {env_user}")
    connection = psycopg2.connect(host=env_host, port=env_port, database=env_database, user=env_user, password=env_password) 
    return connection

def get_notif_data():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Получаем активные уведомления с telegram_id из таблицы user
    cursor.execute("""
                    SELECT json_agg(n)
                    FROM (
                        SELECT
                            n.notification_id,
                            n.user_id,
                            u.telegram_id,
                            n.event_date,
                            n.notif_user_time,
                            n.notif_time,
                            n.notif_status,
                            n.event_name
                        FROM evt.notification n
                        INNER JOIN evt.user u ON n.user_id = u.user_id
                        WHERE n.notif_status = 'Active'
                        AND u.telegram_id IS NOT NULL
                    ) n;
                  """)
    
    result = cursor.fetchone()
    print(f"\nРезультат запроса: {result}")
    
    if result is None or result[0] is None:
        print("Нет данных для обработки")
        rows = []
    else:
        rows = result[0]
    
    connection.commit() 
    cursor.close() 
    connection.close()
    
    print("\n=== Полученные данные из БД ===")
    print(f"Всего уведомлений: {len(rows) if rows else 0}")
    for row in (rows if rows else []):
        print(f"\nУведомление ID: {row['notification_id']}")
        print(f"Событие: {row['event_name']}")
        print(f"Telegram ID пользователя: {row['telegram_id']}")
        print(f"Дата события: {row['event_date']}")
        print(f"Время уведомления (минут до события): {row['notif_user_time']}")
        print(f"Статус: {row['notif_status']}")
    print("==============================\n")
    
    return rows if rows else []

async def send_notification(chat_id, event_name, event_time, notif_time):
    bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
    try:
        message = f"Напоминание! Событие '{event_name}' начнется через {notif_time} минут ({event_time})"
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return False

def update_notification_status(notification_id, status):
    connection = db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE evt.notification 
            SET notif_status = %s 
            WHERE notification_id = %s
        """, (status, notification_id))
        connection.commit()
        print(f"Статус уведомления {notification_id} обновлен на '{status}'")
    except Exception as e:
        print(f"Ошибка при обновлении статуса уведомления: {e}")
    finally:
        cursor.close()
        connection.close()

async def check_and_send_notifications():
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_tz)
    print(f"\n=== Проверка уведомлений ===")
    print(f"Текущее время (МСК): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    notifications = get_notif_data()
    
    for notification in notifications:
        if not notification['telegram_id']:
            print(f"\nПропуск уведомления {notification['notification_id']}: нет Telegram ID")
            continue
            
        event_time = datetime.fromisoformat(notification['event_date'])
        event_time = moscow_tz.localize(event_time)
        
        # Вычисляем время уведомления (за указанное количество минут до события)
        notification_time = event_time - timedelta(minutes=notification['notif_user_time'])
        
        print(f"\nАнализ уведомления {notification['notification_id']}:")
        print(f"Время события: {event_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Время уведомления (за {notification['notif_user_time']} мин до события): {notification_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Текущее время: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Если время события уже прошло, меняем статус на Done
        if current_time > event_time:
            update_notification_status(notification['notification_id'], 'Done')
            print(f"Время события прошло, статус обновлен на 'Done'")
            continue
            
        # Если текущее время находится между временем уведомления и временем события
        if notification_time <= current_time <= event_time:
            print("Уведомление должно быть отправлено!")
            if await send_notification(notification['telegram_id'], 
                               notification['event_name'],
                               event_time.strftime('%H:%M'),
                               notification['notif_user_time']):
                print(f"Уведомление для события '{notification['event_name']}' успешно отправлено")
            else:
                print("Ошибка при отправке уведомления")
        else:
            print("Уведомление пока не требуется отправлять")
    
    print("\n=== Проверка завершена ===\n")

async def main():
    print("Запуск сервиса уведомлений...")
    try:
        while True:
            try:
                await check_and_send_notifications()
                print("Ожидание 15 минут до следующей проверки...")
                await asyncio.sleep(900)  # 900 секунд = 15 минут
            except asyncio.CancelledError:
                print("\nПолучен сигнал завершения работы...")
                break
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                print("Повторная попытка через 1 минуту...")
                await asyncio.sleep(60)  # В случае ошибки ждем 1 минуту перед повторной попыткой
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    finally:
        print("Завершение работы сервиса уведомлений...")

def signal_handler():
    print("\nПолучен сигнал завершения работы...")
    for task in asyncio.all_tasks():
        task.cancel()

if __name__ == "__main__":
    try:
        # Устанавливаем обработчик сигналов
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
        
        # Запускаем основную программу
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    finally:
        print("Завершение работы...")
