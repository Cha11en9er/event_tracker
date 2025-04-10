import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
import pytz

load_dotenv()

def db_connection():
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return connection

def check_and_update_events():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        # Получаем все события со статусом Future или Going
        cursor.execute("""
            SELECT 
                event_id,
                event_date,
                event_duration,
                event_status,
                event_name
            FROM evt.event
            WHERE event_status IN ('Future', 'Going')
        """)
        
        events = cursor.fetchall()
        moscow_tz = pytz.timezone('Europe/Moscow')
        current_time = datetime.now(moscow_tz)

        for event in events:
            # Правильное преобразование времени события в московский часовой пояс
            event_start = moscow_tz.localize(event['event_date'])
            event_duration = event['event_duration']
            event_end = event_start + timedelta(minutes=event_duration)
            
            print(f"Текущее время (МСК): {current_time}")
            print(f"Время начала события (МСК): {event_start}")
            print(f"Время окончания события (МСК): {event_end}")

            
            # Проверяем, идет ли событие сейчас
            if event_start <= current_time <= event_end:
                if event['event_status'] != 'Going':
                    cursor.execute("""
                        UPDATE evt.event
                        SET event_status = 'Going'
                        WHERE event_id = %s
                    """, (event['event_id'],))
                    print(f"Событие '{event['event_name']}' началось")
            
            # Проверяем, закончилось ли событие
            elif current_time > event_end:
                if event['event_status'] != 'Past':
                    cursor.execute("""
                        UPDATE evt.event
                        SET event_status = 'Past'
                        WHERE event_id = %s
                    """, (event['event_id'],))
                    print(f"Событие '{event['event_name']}' завершено")

                    cursor.execute("""
                        INSERT INTO evt.event_feedback 
                        (event_feedback_id, event_id, event_feedback_status)
                        VALUES (DEFAULT, %s, 'Unsent')
                    """, (event['event_id'],))
        
        connection.commit()
        print(f"Проверка завершена: {datetime.now(moscow_tz)}")
        
    except Exception as e:
        print(f"Ошибка при обновлении статусов: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

def main():
    print("Запуск сервиса проверки статусов событий...")
    while True:
        try:
            check_and_update_events()
            # Проверяем каждую минуту
            time.sleep(60)
        except Exception as e:
            print(f"Ошибка в главном цикле: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
