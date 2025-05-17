from flask import render_template, Blueprint, session
import psycopg2, psycopg2.extras
from datetime import datetime
import re
import locale

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
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
        MONTHS = {
            1: 'Января',
            2: 'Февраля',
            3: 'Марта',
            4: 'Апреля',
            5: 'Мая',
            6: 'Июня',
            7: 'Июля',
            8: 'Августа',
            9: 'Сентября',
            10: 'Октября',
            11: 'Ноября',
            12: 'Декабря'
        }
        
        date_obj = datetime.fromisoformat(date_str)
        day = date_obj.day
        month = MONTHS[date_obj.month]
        year = date_obj.year
        return f"{day} {month}"

    cursor.execute('''
                    SELECT
                        json_build_object(
                            'event_id', e.event_id,
                            'event_date', e.event_date,
                            'event_start_time', e.event_start_time,
                            'event_end_time', e.event_end_time,
                            'event_time', e.event_duration,
                            'event_name', e.event_name,
                            'event_type_name', et.event_type_name,
                            'description', e.description,
                            'event_status', e.event_status,
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
                        e.event_id, e.event_date, e.event_start_time, e.event_end_time, e.event_duration, e.event_name, et.event_type_name, e.description, e.event_status;
    ''', (event_id_from_schedule,))
    event_dict = cursor.fetchone()

    event_data = event_dict[0]
    event_data['description'] = add_hyperlinks(event_data['description'])
    event_data['formatted_time'] = format_date(event_data['event_date'])

    cursor.execute('''
    SELECT 
        json_build_object(
            'is_participant', CASE WHEN ep.event_participation_id IS NOT NULL THEN true ELSE false END,
            'role_name', COALESCE(r.role_name, 'Unsubscribed')
        ) as user_event_info
    FROM 
        evt.event e
    LEFT JOIN evt.event_participation ep ON 
        ep.event_id = e.event_id AND 
        ep.user_id = %s
    LEFT JOIN evt.role r ON 
        ep.user_event_role_id = r.role_id
    WHERE 
        e.event_id = %s
    ''', (user_session_id, event_id_from_schedule))
    user_event_info = cursor.fetchone()[0]

    print((user_session_id, event_id_from_schedule))
    print(user_event_info)

    event_data['event_participation'] = str(user_event_info['is_participant'])

    if session['telegram_id'] is None:
        event_data['user_telegram_id'] = 'False'
    else:
        event_data['user_telegram_id'] = session['telegram_id']

    event_data['user_current_id'] = session['id']
    event_data['user_role'] = session['role']
    event_data['user_event_role'] = user_event_info['role_name']

    print('###############', event_data)

    return render_template('current_event.html', data = event_data)