from flask import request, redirect, Blueprint, url_for, flash
import psycopg2, psycopg2.extras

end_event_blueprint = Blueprint('end_event', __name__)

@end_event_blueprint.route('/end_event', methods=['POST'])
def end_event():
    connection = end_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    event_id = request.form['event_id']
    
    try:
        cursor.execute("""
            UPDATE evt.event 
            SET event_status = 'Past' 
            WHERE event_id = %s 
            RETURNING event_name
        """, (event_id,))
        
        event_name = cursor.fetchone()['event_name']
        connection.commit()
        flash(f'Мероприятие "{event_name}" завершено')
        
    except Exception as e:
        connection.rollback()
        flash(f'Ошибка при завершении мероприятия: {str(e)}')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('current_event.current_event', event_id_from_schedule=event_id))