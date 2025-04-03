from flask import request, jsonify, Blueprint, session
from datetime import datetime, time
import psycopg2, psycopg2.extras

search_event_blueprint = Blueprint('search_event', __name__)

@search_event_blueprint.route('/get_search_event', methods = ['GET'])
def get_search_event():
    connection = search_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    search_info = request.args.get('search_info')

    print(search_info)

    return True

    # if 'loggedin' in session:
    #     cursor.execute(f"""
    #                     SELECT
    #                         e.event_date,
    #                         e.event_name,
    #                         e.discription,
    #                         et.event_type_name,
    #                         COUNT(ep.event_participation_id),
    #                         e.event_id,
    #                         e.event_time
    #                     FROM
    #                         evt.event AS e
    #                     INNER JOIN evt.event_type AS et ON
    #                         e.event_type_id = et.event_type_id
    #                     LEFT JOIN evt.event_participation ep ON
    #                         e.event_id = ep.event_id
    #                     WHERE e.event_name LIKE '%{search_info}%'
    #                     OR e.discription LIKE '%{search_info}%'
    #                     GROUP BY
    #                         e.event_id,
    #                         et.event_type_name
    #                     ORDER BY
    #                         e.event_date
    #                     """)
    #     rows = cursor.fetchall()

    #     cursor.execute('''
    #         SELECT 
    #             ep.event_id
    #         FROM evt.event_participation as ep
    #         WHERE ep.user_id = %s;
    #         ''', (session['id'],))
    #     user_participation = cursor.fetchall()

    #     cursor.close()
    #     connection.close()

    #     for i in range(len(rows)):
    #         datetime_date = datetime.strptime(str(rows[i][0]), '%Y-%m-%d')
    #         formatted_date = datetime_date.strftime('%d %B %Y года')
    #         formatted_date = formatted_date.lstrip('0')
    #         rows[i][0] = formatted_date

    #         if isinstance(rows[i][6], time):
    #             rows[i][6] = rows[i][6].strftime('%H:%M')
    #         else:
    #             rows[i][6] = 'Время не указано'

    #     data = [
    #                 {
    #                     'event_date': row[0],
    #                     'event_name': row[1], 
    #                     'event_disc': row[2], 
    #                     'event_type': row[3], 
    #                     'participation_count': row[4], 
    #                     'event_id': row[5], 
    #                     'user_id': session['id'], 
    #                     'user_participation': user_participation, 
    #                     'event_time': row[6]
    #                 } for row in rows
    #             ]

    #     return jsonify(data)