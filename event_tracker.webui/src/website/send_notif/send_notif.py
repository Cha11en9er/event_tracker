from flask import Blueprint, request
import requests
from dotenv import load_dotenv
import os
import psycopg2, psycopg2.extras
from datetime import datetime, timedelta, timezone

send_notif_blueprint = Blueprint('send_notif', __name__)

@send_notif_blueprint.route('/send_notif', methods=['POST'])
def take_data_from_js():
    data = request.json
    telegram_id = data.get('telegramId')
    user_id = data.get('userId')
    selected_time = data.get('selectedTime')

    print(f"Received data - Telegram ID: {telegram_id}, User ID: {user_id}, Selected Time: {selected_time}")


# load_dotenv()
# offset = timezone(timedelta(hours=3))  # Смещение на 3 часа
# current_time = datetime.now(offset)

# def db_connection():
#     env_host = os.getenv('DB_HOST')
#     env_port = os.getenv('DB_PORT')
#     env_database = os.getenv('DB_NAME')
#     env_user = os.getenv('DB_USER')
#     env_password = os.getenv('DB_PASSWORD')
#     connection = psycopg2.connect(host=env_host, port=env_port, database=env_database, user=env_user, password=env_password) 
#     return connection

# def take_data_from_db():
#     connection = db_connection()
#     cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

#     cursor.execute("""
#                     select
#                         *
#                     from
#                         evt.event""")

#     data = cursor.fetchall()
#     return data

# def calculate_time(event_data, current_time):
#     env_tg_token = os.getenv('TG_BOT_TOKEN')
#     chat_id = "508607571"

#     now_month = current_time.month
#     now_day = current_time.day
#     now_hour = current_time.hour
#     now_minut = current_time.minute
#     for i in range(len(event_data)):
#         if event_data[i][5]:
#             event_start_time = str(event_data[i][5]).split(':')
#             event_start_date = str(event_data[i][1]).split('-')
#             event_start_hour, event_start_minut = int(event_start_time[0]), int(event_start_time[1])
#             event_start_month, event_start_day = int(event_start_date[1]), int(event_start_date[2])
#             if (event_start_month == now_month) and (event_start_day == now_day) and (((now_hour == event_start_hour) and (0 < event_start_minut - now_minut <= 15)) or ((event_start_hour - now_hour == 1) and (30 > now_minut - event_start_minut >= 45))):
#                 notif_msg = f'{event_data[i][2]} начнётся меньше чем через 15 минут'
#                 url = f"https://api.telegram.org/bot{env_tg_token}/sendMessage?chat_id={chat_id}&text={notif_msg}"
#                 requests.get(url).json()


# event_data = take_data_from_db()
# calculate_time(event_data, current_time)


# print('скрипт с мониторингом ивентов включился')