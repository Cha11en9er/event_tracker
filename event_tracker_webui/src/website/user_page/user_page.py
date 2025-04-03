from flask import Blueprint, render_template, session, jsonify, request
import json
import psycopg2, psycopg2.extras
import requests
import os
from dotenv import load_dotenv

load_dotenv()

user_page_blueprint = Blueprint('user_page', __name__)

def db_connection():
    env_host = os.getenv('DB_HOST')
    env_port = os.getenv('DB_PORT')
    env_database = os.getenv('DB_NAME')
    env_user = os.getenv('DB_USER')
    env_password = os.getenv('DB_PASSWORD')
    connection = psycopg2.connect(host=env_host, port=env_port, database=env_database, user=env_user, password=env_password) 
    return connection

@user_page_blueprint.route('/verify_telegram_id', methods=['POST'])
def verify_telegram_id():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        user_id = session.get('id')

        if not chat_id or not user_id:
            return jsonify({'success': False, 'message': 'Отсутствуют необходимые данные'})

        connection = db_connection()
        cursor = connection.cursor()

        # Проверяем, существует ли chat_id в таблице subscribe
        cursor.execute("""
            SELECT chat_id FROM evt.subscribe 
            WHERE chat_id = %s
        """, (chat_id,))
        
        if cursor.fetchone() is None:
            return jsonify({'success': False, 'message': 'ID чата не найден. Убедитесь, что вы начали диалог с ботом'})

        # Обновляем telegram_id пользователя
        cursor.execute("""
            UPDATE evt."user"
            SET telegram_id = %s
            WHERE user_id = %s
        """, (chat_id, user_id))

        connection.commit()

        # Отправляем сообщение через бота
        bot_token = os.getenv('TG_BOT_TOKEN')
        message = 'Отправка сообщений настроена, можете подключать уведомления на мероприятия'
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': message
        }
        response = requests.post(url, data=data)

        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Telegram ID успешно привязан'})
        else:
            return jsonify({'success': False, 'message': 'Ошибка при отправке сообщения'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Произошла ошибка: {str(e)}'})
    finally:
        if 'connection' in locals():
            connection.close()

@user_page_blueprint.route('/user_page/<int:user_id_from_form>', methods = ['GET', 'POST'])
def user_page(user_id_from_form):
    connection = user_page_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:

        cursor.execute("""
                        SELECT
                            e.event_name,
                            u.fullname,
                            u.email,
                            u.telegram_id
                        FROM evt."user" AS u
                        LEFT JOIN evt.event_participation AS ep
                        ON u.user_id = ep.user_id
                        LEFT JOIN evt."event" AS e
                        ON ep.event_id = e.event_id 
                        WHERE 
                            u.user_id = %s;
                        """ % user_id_from_form)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description] # получение названий столбцов
        connection.close()

        user_raw_data = [dict(zip(columns, row)) for row in rows]

        user_data = {}
        for item in user_raw_data:
            fullname = item['fullname']
            email = item['email']
            telegram_id = item['telegram_id']
            event_name = item['event_name']

            if (fullname, email, telegram_id) not in user_data:
                user_data[(fullname, email, telegram_id)] = {
                    'fullname': fullname,
                    'email': email,
                    'telegram_id': telegram_id,
                    'event_name': set()
                }

            user_data[(fullname, email, telegram_id)]['event_name'].add(event_name)
            

        user_data = list(user_data.values())
        user_data[0]['session_user_id'] = session['id']
        user_data[0]['page_user_id'] = user_id_from_form

    print(user_data)

    return render_template('user_page.html', user_data = user_data)