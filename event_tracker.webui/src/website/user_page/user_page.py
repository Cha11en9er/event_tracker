from flask import Blueprint, render_template, session, jsonify
import json
import psycopg2, psycopg2.extras

user_page_blueprint = Blueprint('user_page', __name__)

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
        
        print('#######################')
        print(rows)

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


        # print(user_data)

    return render_template('user_page.html', user_data = user_data)