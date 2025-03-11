from flask import render_template, Blueprint, session
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
                            'event_date', e.event_date,
                            'event_time', e.event_time,
                            'event_name', e.event_name,
                            'event_type_id', e.event_type_id,
                            'description', e.description,
                            'fullname', array_agg(u.fullname),
                            'user_id', array_agg(u.user_id)
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
                    WHERE
                        e.event_id = %s
                    GROUP BY
                        e.event_date, e.event_time, e.event_name, e.event_type_id, e.description;
    ''', (event_id_from_schedule,))
    event_dict = cursor.fetchone()

    cursor.execute('''
                    SELECT ep.event_participation_id
                    FROM evt.event_participation AS ep
                    WHERE 1 = 1
                    AND ep.user_id = %s
                    AND ep.event_id = %s
    ''', (user_session_id, event_id_from_schedule, ))
    user_current_event_participation = cursor.fetchone()

    event_data = event_dict[0]

    event_data['description'] = add_hyperlinks(event_data['description'])

    if user_current_event_participation is None:
        event_data['event_participation'] = 'False'
    else:
        event_data['event_participation'] = 'True'

    event_data['formatted_time'] = format_date(event_data['event_date'])

    if not event_data['user_id'] or all(user_id is None for user_id in event_data['user_id']):
        event_data['fullname'] = ['В мероприятии нету участников. Вы можете стать первым']
    
    if session['telegram_id'] is None:
        event_data['user_telegram_id'] = 'False'
    else:
        event_data['user_telegram_id'] = session['telegram_id']

    event_data['user_current_id'] = session['id']

    print(event_data)

    return render_template('current_event.html', data = event_data)