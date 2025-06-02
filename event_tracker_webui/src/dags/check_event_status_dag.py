from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pytz

def update_event_statuses(**kwargs):
    # Get connection from Airflow
    pg_hook = PostgresHook(postgres_conn_id='event_tracker_db_schema_evt')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    # Получаем текущее время в московском часовом поясе
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_moscow_time = datetime.now(moscow_tz)

    cursor.execute("SELECT e.event_id, e.event_name, e.event_date, event_duration FROM evt.event as e where e.event_status = 'Future';")
    events = cursor.fetchall()
    
    for event in events:
        event_id, event_name, event_date, event_duration = event
        
        # Конвертируем время начала события в московское
        event_start = moscow_tz.localize(event_date)
        # Вычисляем время окончания события
        event_end = event_start + timedelta(minutes=event_duration)
        
        # Обновляем статус события
        if current_moscow_time > event_end:
            cursor.execute("UPDATE evt.event SET event_status = 'Past' WHERE event_id = %s", (event_id,))
            print(f"Event {event_name} (ID: {event_id}) marked as Past")
        elif current_moscow_time >= event_start:
            cursor.execute("UPDATE evt.event SET event_status = 'Current' WHERE event_id = %s", (event_id,))
            print(f"Event {event_name} (ID: {event_id}) marked as Current")
    
    # Фиксируем изменения в базе данных
    conn.commit()
    cursor.close()
    conn.close()

with DAG(
    dag_id="check_event_status_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="*/1 * * * *",  # Каждую минуту
    catchup=False,
) as dag:
    update_status = PythonOperator(
        task_id="update_event_statuses",
        python_callable=update_event_statuses,
    )
