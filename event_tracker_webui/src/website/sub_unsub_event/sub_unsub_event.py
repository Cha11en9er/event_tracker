from flask import request, redirect, url_for, Blueprint
import psycopg2, psycopg2.extras

sub_unsub_event_blueprint = Blueprint('sub_unsub', __name__)

@sub_unsub_event_blueprint.route('/subscribe_to_event', methods = ['POST'])
def subscribe_to_event():
    connection = sub_unsub_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    event_id = request.form.get('event_id_from_js')
    user_id = request.form.get('user_id_from_js')

    cursor.execute('''
                    insert into
                        evt.event_participation
                    (event_id, user_id)
                    values(%s, %s)''', (event_id, user_id, ))
    connection.commit() 
    cursor.close() 
    connection.close()

    return redirect(url_for('schedule_menu.schedule'))

@sub_unsub_event_blueprint.route('/unsubscribe_from_event', methods = ['POST'])
def unsubscribe_from_event():
    connection = sub_unsub_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    event_id = request.form.get('event_id_from_js')
    user_id = request.form.get('user_id_from_js')

    cursor.execute('''
                    delete from 
                        evt.event_participation
                    where
                        event_id = %s
                    and 
                        user_id = %s''',
                    (event_id, user_id, ))
    connection.commit() 
    cursor.close() 
    connection.close()

    return redirect(url_for('schedule_menu.schedule'))