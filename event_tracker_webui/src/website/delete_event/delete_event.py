from flask import request, redirect, Blueprint, url_for, flash
import psycopg2, psycopg2.extras

delete_event_blueprint = Blueprint('delete_event', __name__)

@delete_event_blueprint.route('/delete_event', methods = ['POST', 'GET'])
def delete_event():
    delete_event_id = request.form['delete_event_id']
    delete_event_name = request.form['delete_event_name']
    connection = delete_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    try:
        # Удаляем все уведомления, связанные с событием
        cursor.execute("""
            DELETE FROM evt.notification
            WHERE event_id = %s
        """, (delete_event_id,))

        # Удаляем все записи об участии в событии
        cursor.execute("""
            DELETE FROM evt.event_participation
            WHERE event_id = %s
        """, (delete_event_id,))

        # Удаляем все роли в событии
        cursor.execute("""
            DELETE FROM evt.event_role
            WHERE event_id = %s
        """, (delete_event_id,))

        # Теперь можно удалить само событие
        cursor.execute("""
            DELETE FROM evt.event
            WHERE event_id = %s
        """, (delete_event_id,))

        connection.commit()
        flash(f'Вы удалили мероприятие {delete_event_name}')

    except Exception as e:
        connection.rollback()
        flash(f'Ошибка при удалении мероприятия: {str(e)}')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('schedule_menu.schedule'))