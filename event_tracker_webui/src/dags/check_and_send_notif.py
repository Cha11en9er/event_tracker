import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def db_connection():
    env_host = os.getenv('DB_HOST')
    env_port = os.getenv('DB_PORT')
    env_database = os.getenv('DB_NAME')
    env_user = os.getenv('DB_USER')
    env_password = os.getenv('DB_PASSWORD')
    connection = psycopg2.connect(host=env_host, port=env_port, database=env_database, user=env_user, password=env_password) 
    return connection

def check_and_send_notif():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("""
                    SELECT e.event_id, e.event_name, e.event_date, e.event_duration
                   """)

