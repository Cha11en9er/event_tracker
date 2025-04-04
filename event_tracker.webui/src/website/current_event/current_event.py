from flask import render_template, Blueprint, session, request, jsonify
import psycopg2, psycopg2.extras
from datetime import datetime

import re

current_event_blueprint = Blueprint('current_event', __name__)

@current_event_blueprint.route('/current_event/<int:event_id_from_schedule>', methods = ['GET', 'POST'])
def current_event(event_id_from_schedule):
    connection = current_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    user_session_id = session['id']

    def add_hyperlinks(text):
        url_pattern = re.compile(r'(https?://\S+)')

        def replace_with_link(match):
            url = match.group(0)
            return f"<a href='{url}' target='_blank' rel='noopener noreferrer'>{url}</a>"

        return url_pattern.sub(replace_with_link, text)
    
    def format_date(date_str):
        date_obj = datetime.fromisoformat(date_str)
        day = date_obj.day
        month = date_obj.strftime('%B')
        return f"{day} {month}"

    cursor.execute('''
                    SELECT
                        json_build_object(
                            'event_id', e.event_id,
                            'event_date', e.event_date,
                            'event_start_time', e.event_start_time,
                            'event_end_time', e.event_end_time,
                            'event_name', e.event_name,
                            'event_type_name', et.event_type_name,
                            'description', e.description,
                            'participants', array_agg(
                                json_build_object(
                                    'fullname', u.fullname,
                                    'user_id', u.user_id
                                )
                            ),
                            'total_participants', COUNT(u.user_id)  -- Добавляем общее количество участников
                        ) AS event
                    FROM
                        evt."event" e
                    LEFT JOIN
                        evt.event_participation AS ep
                    ON
                        e.event_id = ep.event_id
                    LEFT JOIN
                        evt."user" AS u
                    ON
                        ep.user_id = u.user_id
                    LEFT JOIN 
                        evt.event_type AS et
                    ON
                        e.event_type_id = et.event_type_id 
                    WHERE
                        e.event_id = %s
                    GROUP BY
                        e.event_id, e.event_date, e.event_start_time, e.event_end_time, e.event_name, et.event_type_name, e.description;
    ''', (event_id_from_schedule,))
    event_dict = cursor.fetchone()

    cursor.execute('''
    SELECT json_build_object(
        'participation', (
            SELECT ep.event_participation_id
            FROM evt.event_participation AS ep
            WHERE ep.user_id = %s AND ep.event_id = %s
        ),
        'role', (
            SELECT r.role_description
            FROM evt.role as r
            WHERE r.user_id = %s
        ),
        'telegram_id', (
            SELECT u.telegram_id
            FROM evt.user as u
            WHERE u.user_id = %s
        )
        ) as user_data
    ''', (user_session_id, event_id_from_schedule, user_session_id, user_session_id))
    user_data = cursor.fetchone()[0]

    event_data = event_dict[0]

    event_data['description'] = add_hyperlinks(event_data['description'])

    event_participation = user_data.get('participation')
    user_role = user_data.get('role')
    telegram_id = user_data.get('telegram_id')

    print(telegram_id)

    if event_participation is None:
        event_data['event_participation'] = 'False'
    else:
        event_data['event_participation'] = 'True'

    event_data['formatted_time'] = format_date(event_data['event_date'])

    if telegram_id is None:
        event_data['user_telegram_id'] = 'False'
    else:
        event_data['user_telegram_id'] = telegram_id

    event_data['user_current_id'] = session['id']
    event_data['user_role'] = user_role
    event_data['current_user_role_id'] = session['id']

    print(event_data)

    return render_template('current_event.html', data = event_data)

@current_event_blueprint.route('/finish_event', methods=['POST'])
def finish_event():
    if request.method == 'POST':
        data = request.get_json()
        event_id = data.get('event_id')
        
        print(f'Ивент {event_id} закончился')
        
        connection = current_event_blueprint.db_connection()
        cursor = connection.cursor()
        
        try:
            # Обновляем статус мероприятия
            cursor.execute("""
                UPDATE evt.event 
                SET status = 'Finished' 
                WHERE event_id = %s
            """, (event_id,))
            
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            print(f"Ошибка при завершении мероприятия: {e}")
            return jsonify({'success': False, 'error': str(e)})
        finally:
            cursor.close()
            connection.close()