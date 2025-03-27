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

        # Получаем типы событий
        cursor.execute('''
            SELECT event_type_id, event_type_name 
            FROM evt.event_type 
            ORDER BY event_type_name;
        ''')
        event_types = cursor.fetchall()

        # Получаем активные события (будущие)
        cursor.execute('''
            SELECT json_agg(subquery)
            FROM (
                SELECT
                    e.event_date,
                    e.event_name,
                    COALESCE(e.description, 'нету описания') AS description,
                    COALESCE(et.event_type_name, 'нет типа') AS event_type_name,
                    e.event_id,
                    e.event_time
                FROM
                    evt.event AS e
                LEFT JOIN
                    evt.event_type AS et ON e.event_type_id = et.event_type_id
                WHERE 
                    e.event_name ILIKE %s
                    AND e.event_date >= CURRENT_DATE
                ORDER BY
                    e.event_date
            ) AS subquery;
        ''', ('%' + search_info + '%',))
        active_events = cursor.fetchone()[0]

        # Получаем прошедшие события
        cursor.execute('''
            SELECT json_agg(subquery)
            FROM (
                SELECT
                    e.event_date,
                    e.event_name,
                    COALESCE(et.event_type_name, 'нет типа') AS event_type_name,
                    e.event_id
                FROM
                    evt.event AS e
                LEFT JOIN
                    evt.event_type AS et ON e.event_type_id = et.event_type_id
                WHERE 
                    e.event_date < CURRENT_DATE
                ORDER BY
                    e.event_date DESC
                LIMIT 50
            ) AS subquery;
        ''')
        past_events = cursor.fetchone()[0] or []

        user_data = session['id']

        cursor.close()
        connection.close()

        # Форматирование даты
        def format_date(date_str):
            date_obj = datetime.fromisoformat(date_str)
            day = date_obj.day
            month = date_obj.strftime('%B')
            return f"{day} {month}"

        # Форматируем даты для активных событий
        if active_events:
            for event in active_events:
                event['formatted_time'] = format_date(event['event_date'])

            # Пагинация
            total_items = len(active_events)
            total_pages = (total_items + items_per_page - 1) // items_per_page
            start_index = (page - 1) * items_per_page
            end_index = start_index + items_per_page
            paginated_data = active_events[start_index:end_index]
        else:
            paginated_data = []
            total_pages = 1

        # Форматируем даты для прошедших событий
        for event in past_events:
            event['formatted_time'] = format_date(event['event_date'])

        return render_template('schedule.html', 
                             events=paginated_data, 
                             past_events=past_events,
                             total_pages=total_pages, 
                             current_page=page, 
                             search_info=search_info, 
                             user_data=user_data, 
                             no_results=not active_events,
                             event_type=event_types)

    return render_template('schedule.html', 
                         events=[], 
                         past_events=[],
                         total_pages=0,  
                         current_page=1, 
                         search_info='', 
                         no_results=True,
                         event_type=[])
