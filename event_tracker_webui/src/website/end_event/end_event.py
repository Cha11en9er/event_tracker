from flask import request, redirect, Blueprint, url_for, flash
import psycopg2, psycopg2.extras

end_event_blueprint = Blueprint('end_event', __name__)

@end_event_blueprint.route('/end_event', methods=['POST'])
def end_event():
    connection = end_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    event_id = int(request.form['event_id'])
    
    try:
        cursor.execute("""
            UPDATE evt.event 
            SET event_status = 'Past' 
            WHERE event_id = %s;
        """, (event_id,))
        
        cursor.execute("""
            INSERT INTO evt.event_feedback
            (event_feedback_id, event_id, event_feedback_status)
            VALUES (DEFAULT, %s, 'Unsent')
        """, (event_id,))

        connection.commit()
        flash(f'Мероприятие завершено')
        
    except Exception as e:
        print(e)
        connection.rollback()
        flash(f'Ошибка при завершении мероприятия: {str(e)}')
    finally:
        cursor.close()
        connection.close()
    
    return redirect(url_for('current_event.current_event', event_id_from_schedule=event_id))