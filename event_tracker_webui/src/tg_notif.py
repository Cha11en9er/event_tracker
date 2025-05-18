from datetime import datetime, timedelta
import pytz
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from dotenv import load_dotenv
import psycopg2, psycopg2.extras
import os
import time
import asyncio
import signal
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

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
    # print(f"\nРезультат запроса: {result}")
    
    if result is None or result[0] is None:
        # print("Нет данных для обработки")
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
        message = f"Напоминание! Событие '{event_name}' начнется меньше чем через {notif_time} минут"
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

async def send_feedback(chat_id, message):
    bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return False
    

    
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
        
        # Если текущее время находится между временем уведомления и временем события
        if notification_time <= current_time <= event_time:
            print("Уведомление должно быть отправлено!")
            if await send_notification(notification['telegram_id'], 
                               notification['event_name'],
                               event_time.strftime('%H:%M'),
                               notification['notif_user_time']):
                print(f"Уведомление для события '{notification['event_name']}' успешно отправлено")
                # Сразу помечаем уведомление как выполненное после успешной отправки
                update_notification_status(notification['notification_id'], 'Done')
            else:
                print("Ошибка при отправке уведомления")
        else:
            print("Уведомление пока не требуется отправлять")
    
    print("\n=== Проверка завершена ===\n")

async def handle_feedback_response(update, context):
    query = update.callback_query
    feedback_data = query.data.split('_')
    event_id = feedback_data[1]
    rating = feedback_data[2]
    
    print(f"\nПолучен фидбек: Мероприятие ID {event_id}, Оценка: {rating}")
    
    # Подтверждаем пользователю получение фидбека
    await query.answer(f"Спасибо за ваш отзыв! Вы поставили оценку: {rating}")
    await query.edit_message_text(text=f"Спасибо за ваш отзыв! Вы поставили оценку: {rating}")

async def send_feedback_request(chat_id, event_name, event_id):
    bot = Bot(token=os.getenv('TG_BOT_TOKEN'))
    try:
        keyboard = []
        button_row = []
        for i in range(1, 6):
            callback_data = f"feedback_{event_id}_{i}"
            button_row.append(InlineKeyboardButton(str(i), callback_data=callback_data))
        keyboard.append(button_row)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"Мероприятие '{event_name}' завершено.\nПожалуйста, оцените мероприятие от 1 до 5:"
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup
        )
        return True
    except TelegramError as e:
        print(f"Ошибка при отправке запроса на фидбек: {e}")
        return False

async def check_and_send_feedback():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                ef.event_feedback_id,
                ef.event_id,
                e.event_name,
                array_agg(u.telegram_id) as telegram_ids
            FROM evt.event_feedback ef
            JOIN evt.event e ON ef.event_id = e.event_id
            JOIN evt.event_participation ep ON e.event_id = ep.event_id
            JOIN evt.user u ON ep.user_id = u.user_id
            WHERE ef.event_feedback_status = 'Unsent'
            AND u.telegram_id IS NOT NULL
            GROUP BY ef.event_feedback_id, ef.event_id, e.event_name
        """)
        
        feedback_requests = cursor.fetchall()
        
        for request in feedback_requests:
            success = True
            for telegram_id in request['telegram_ids']:
                if not await send_feedback_request(telegram_id, request['event_name'], request['event_id']):
                    success = False
                    break
            
            if success:
                cursor.execute("""
                    UPDATE evt.event_feedback
                    SET event_feedback_status = 'Sent'
                    WHERE event_feedback_id = %s
                """, (request['event_feedback_id'],))
                connection.commit()
                print(f"Запросы на фидбек для мероприятия '{request['event_name']}' отправлены")
    
    except Exception as e:
        print(f"Ошибка при отправке запросов на фидбек: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

async def main():
    print("Запуск сервиса уведомлений...")
    
    application = Application.builder().token(os.getenv('TG_BOT_TOKEN')).build()
    application.add_handler(CallbackQueryHandler(handle_feedback_response))
    
    try:
        # Запускаем бота в фоновом режиме
        await application.initialize()
        await application.start()
        
        while True:
            try:
                await check_and_send_notifications()
                await check_and_send_feedback()
                print("Ожидание 15 минут до следующей проверки...")
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                print("\nПолучен сигнал завершения работы...")
                break
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                print("Повторная попытка через 1 минуту...")
                await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    finally:
        print("Завершение работы сервиса уведомлений...")
        try:
            await application.stop()
            await application.shutdown()
        except Exception as e:
            print(f"Ошибка при завершении работы бота: {e}")

def signal_handler():
    print("\nПолучен сигнал завершения работы...")
    for task in asyncio.all_tasks():
        task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    finally:
        print("Завершение работы...")
