from flask import render_template, Blueprint, session, jsonify
import psycopg2, psycopg2.extras
from datetime import date, datetime, time
import locale

locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
schedule_menu_blueprint = Blueprint('schedule_menu', __name__)

@schedule_menu_blueprint.route('/schedule')
def schedule():
    connection = schedule_menu_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        print(session)

        data_account = []
        cursor.execute("""
                        select
                            *
                        from
                            evt.event_type;""")
        
        data_account.extend((session['id'], session['username']))
        data_event_type = cursor.fetchall()

        return render_template('schedule.html', account=data_account, event_type=data_event_type)

@schedule_menu_blueprint.route('/get_schedule_data', methods=['GET'])
def get_schedule_data():
    connection = schedule_menu_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        cursor.execute('''
            SELECT
                e.event_date,
                e.event_name,
                e.discription,
                et.event_type_name,
                COUNT(ep.event_participation_id),
                e.event_id,
                e.event_time
            FROM
                evt.event AS e
            INNER JOIN evt.event_type AS et ON
                e.event_type_id = et.event_type_id
            LEFT JOIN evt.event_participation ep ON
                e.event_id = ep.event_id
            GROUP BY
                e.event_id,
                et.event_type_name
            ORDER BY
                e.event_date
        ''')
        rows = cursor.fetchall()

        cursor.execute('''
            SELECT 
                ep.event_id
            FROM evt.event_participation as ep
            WHERE ep.user_id = %s;
        ''', (session['id'],))
        user_participation = cursor.fetchall()

        cursor.close()
        connection.close()

        for i in range(len(rows)):
            datetime_date = datetime.strptime(str(rows[i][0]), '%Y-%m-%d')
            formatted_date = datetime_date.strftime('%d %B %Y года')
            formatted_date = formatted_date.lstrip('0')
            rows[i][0] = formatted_date

            if isinstance(rows[i][6], time):
                rows[i][6] = rows[i][6].strftime('%H:%M')
            else:
                rows[i][6] = 'Время не указано'

        data = [
                    {
                        'event_date': row[0],
                        'event_name': row[1], 
                        'event_disc': row[2], 
                        'event_type': row[3], 
                        'participation_count': row[4], 
                        'event_id': row[5], 
                        'user_id': session['id'], 
                        'user_participation': user_participation, 
                        'event_time': row[6]
                    } for row in rows
                ]

        return jsonify(data)  # Возвращаем данные в формате JSON