from flask import request, redirect, url_for, Blueprint, flash
import psycopg2, psycopg2.extras

create_event_blueprint = Blueprint('create_event', __name__)

@create_event_blueprint.route('/create_event', methods = ['POST'])
def create_event():
    connection = create_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    event_date = request.form['event_date']
    event_start_time = request.form['event_time']
    event_name = request.form['event_name']
    event_description = request.form['event_description']
    event_type = request.form.get('event_type_selection')
    event_duration = request.form.get('event_duration')

    # Преобразуем текстовое значение в минуты
    duration_mapping = {
        '15 минут': 15,
        '30 минут': 30,
        '1 час': 60,
        '2 часа': 120
    }
    duration_minutes = int(duration_mapping.get(event_duration, 0))

    # Расчет времени окончания
    start_hours, start_minutes = map(int, event_start_time.split(':'))
    total_minutes = start_hours * 60 + start_minutes + duration_minutes
    end_hours = total_minutes // 60
    end_minutes = total_minutes % 60
    event_end_time = f"{end_hours:02d}:{end_minutes:02d}"

    event_date = event_date.split('-')
    event_date = event_date[0] + '-' + event_date[1] + '-' + event_date[2] + ' ' + event_start_time + ':00'
    event_status = 'Future'

    cursor.execute("""
                    insert into
                        evt.event
                    (event_id, event_date, event_start_time, event_end_time, event_name, description, event_type_id, event_duration, event_status)
                    values (default, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (event_date, event_start_time, event_end_time, event_name, event_description, event_type, duration_minutes, event_status))

    connection.commit() 
    cursor.close() 
    connection.close()
    
    print((event_date, event_start_time, event_end_time, event_name, event_description, event_type, duration_minutes, event_status))

    flash(f'Вы создали мероприятие {event_name}')

    return redirect(url_for('schedule_menu.schedule'))