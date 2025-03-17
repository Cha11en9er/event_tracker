from flask import render_template, Blueprint, session, request
import psycopg2, psycopg2.extras
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
schedule_menu_blueprint = Blueprint('schedule_menu', __name__)

@schedule_menu_blueprint.route('/schedule', methods=['GET'])
def schedule():
    connection = schedule_menu_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        # Получаем параметры пагинации и поиска
        page = int(request.args.get('page', 1))
        search_info = request.args.get('search_info', '')
        items_per_page = 6

        print(search_info)
        # Получаем данные событий
        cursor.execute('''
            SELECT json_agg(subquery)
            FROM (
                SELECT
                    e.event_date,
                    e.event_name,
                    COALESCE(e.description, 'нету описания') AS description,
                    COALESCE(et.event_type_name, 'нет типа') AS event_type_name,
                    COALESCE(ep_count.participant_count, 0) AS participant_count,
                    e.event_id,
                    e.event_time
                FROM
                    evt.event AS e
                LEFT JOIN
                    evt.event_type AS et ON e.event_type_id = et.event_type_id
                LEFT JOIN (
                    SELECT
                        event_id,
                        COUNT(event_participation_id) AS participant_count
                    FROM
                        evt.event_participation
                    GROUP BY
                        event_id
                ) AS ep_count ON e.event_id = ep_count.event_id
                WHERE e.event_name ILIKE %s
                ORDER BY
                    e.event_date
            ) AS subquery;
        ''', ('%' + search_info + '%',))
        rows = cursor.fetchone()[0]

        user_data = session['id']

        cursor.close()
        connection.close()

        # Форматирование даты
        def format_date(date_str):
            date_obj = datetime.fromisoformat(date_str)
            day = date_obj.day
            month = date_obj.strftime('%B')
            return f"{day} {month}"

        if rows:
            for event in rows:
                event['formatted_time'] = format_date(event['event_date'])

            # Пагинация
            total_items = len(rows)
            total_pages = (total_items + items_per_page - 1) // items_per_page
            start_index = (page - 1) * items_per_page
            end_index = start_index + items_per_page
            paginated_data = rows[start_index:end_index]
        else:
            paginated_data = []
            total_pages = 1

        print('###############')
        print(paginated_data)

        return render_template('schedule.html', events=paginated_data, total_pages=total_pages, current_page=page, search_info=search_info, user_data=user_data, no_results=not rows)

    return render_template('schedule.html', events=[], total_pages=0, current_page=1, search_info='', no_results=True)
