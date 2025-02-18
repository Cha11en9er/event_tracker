from flask import request, redirect, Blueprint, url_for
import psycopg2, psycopg2.extras

delete_event_blueprint = Blueprint('delete_event', __name__)

@delete_event_blueprint.route('/delete_event/<int:event_id_from_form>', methods = ['POST', 'GET'])
def delete_event(event_id_from_form):
    connection = delete_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    print(event_id_from_form)

    cursor.execute("""
                    SELECT evt.fun_event_delete(%s);
                    """ % event_id_from_form)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('schedule_menu.schedule'))