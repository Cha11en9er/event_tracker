from flask import request, redirect, Blueprint, url_for, flash
import psycopg2, psycopg2.extras

delete_event_blueprint = Blueprint('delete_event', __name__)

@delete_event_blueprint.route('/delete_event', methods = ['POST', 'GET'])
def delete_event():
    delete_event_id = request.form['delete_event_id']
    delete_event_name = request.form['delete_event_name']
    connection = delete_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # print(delete_event_id)

    cursor.execute("""
                    DELETE FROM evt.event
                    WHERE event_id = %s;
                    """ % delete_event_id)
    connection.commit()
    cursor.close()
    connection.close()
    flash(f'Вы удалили меропиятие {delete_event_name}')

    return redirect(url_for('schedule_menu.schedule'))