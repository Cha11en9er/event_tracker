from flask import render_template, Blueprint, session
import psycopg2, psycopg2.extras
from flask_socketio import emit
from datetime import date, datetime

schedule_menu_blueprint = Blueprint('schedule_menu', __name__)

@schedule_menu_blueprint.route('/schedule')
def schedule():
    connection = schedule_menu_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:

        cursor.execute("""
                        select
                            *
                        from
                            evt.user
                        where
                            user_id = %s"""
                       , [session['id']])
        
        data_account = cursor.fetchone()
        cursor.execute("""
                        select
                            *
                        from
                            evt.event_type;""")
        data_event_type = cursor.fetchall()
        print('#######################################################', data_account)

        return render_template('schedule.html', account = data_account, event_type = data_event_type)
    
def schedule_socket(socketio_app):
    @socketio_app.on('request_schedule_data')
    def handle_request_schedule_data():
        connection = schedule_menu_blueprint.db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('''
            SELECT
                e.event_date,
                e.event_name,
                e.discription,
                et.event_type_name,
                COUNT(ep.event_participation_id),
                e.event_id
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
        cursor.close()
        connection.close()

        for i in range(len(rows)):
            datetime_date = datetime.strptime(str(rows[i][0]), '%Y-%m-%d')
            formatted_date = datetime_date.strftime('%d %B %Y года')
            formatted_date = formatted_date.lstrip('0')
            rows[i][0] = formatted_date

        data = [{'event_date': row[0], 'event_name': row[1], 'event_disc': row[2], 'event_type': row[3], 'participation_count': row[4], 'event_id': row[5], 'user_id': session['id']} for row in rows]
        
        emit('schedule_data', data)