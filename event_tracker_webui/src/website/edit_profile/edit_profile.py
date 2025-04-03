from flask import request, Blueprint, jsonify, session
import psycopg2, psycopg2.extras
import requests

edit_profile_blueprint = Blueprint('edit_profile', __name__)

@edit_profile_blueprint.route('/edit_profile', methods=['POST'])
def edit_profile():
    data_from_js=request.get_json()
    
    connection=edit_profile_blueprint.db_connection()
    cursor=connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    user_fullname=data_from_js['fullname']
    user_email=data_from_js['email']
    user_telegram_id=data_from_js['telegram_id']
    user_password=data_from_js['password']
    user_id=data_from_js['user_id']

    cursor.execute("""
                    UPDATE evt.user
                    SET fullname = %s,
                        email = %s,
                        telegram_id = %s,
                        sys_changed_at = CURRENT_TIMESTAMP(0)::timestamp without time zone,
                        sys_changed_by = %s
                    WHERE user_id = %s;
                    """, (user_fullname, user_email, user_telegram_id, user_id, user_id))

    connection.commit() 
    
    cursor.execute("SELECT fullname, email, telegram_id FROM evt.user WHERE user_id = %s", (user_id,))
    updated_user_data = cursor.fetchone()

    session['fullname'] = updated_user_data[0]
    session['telegram_id'] = updated_user_data[2]

    cursor.close()
    connection.close()

    return jsonify({
        'fullname': updated_user_data['fullname'],
        'email': updated_user_data['email'],
        'telegram_id': updated_user_data['telegram_id']
    })


@edit_profile_blueprint.route('/verify_telegram_id', methods=['POST'])
def verify_telegram_id():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        user_id = session.get('id')

        if not chat_id or not user_id:
            return jsonify({'success': False, 'message': 'Отсутствуют необходимые данные'})

        connection = edit_profile_blueprint.db_connection()
        cursor = connection.cursor()

        # Проверяем, существует ли chat_id в таблице subscribe
        cursor.execute("""
            SELECT chat_id FROM evt.subscribe 
            WHERE chat_id = %s
        """, (chat_id,))
        
        if cursor.fetchone() is None:
            return jsonify({'success': False, 'message': 'Введён некорекнтный id'})

        # Обновляем telegram_id пользователя
        cursor.execute("""
            UPDATE evt."user"
            SET telegram_id = %s
            WHERE user_id = %s
        """, (chat_id, user_id))

        connection.commit()

        # Обновляем telegram_id в сессии
        session['telegram_id'] = chat_id

        # Отправляем сообщение через бота
        bot_token = edit_profile_blueprint.config['TG_BOT_TOKEN']
        message = 'Отправка сообщений настроена, можете подключать уведомления на мероприятия'
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': message
        }
        response = requests.post(url, data=data)

        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Введён правильный id. Проверьте телеграм'})
        else:
            return jsonify({'success': False, 'message': 'Введён некорекнтный id'})

    except Exception as e:
        return jsonify({'success': False, 'message': 'Введён некорекнтный id'})
    finally:
        if 'connection' in locals():
            connection.close()
