from flask import request, redirect, url_for, Blueprint
import psycopg2, psycopg2.extras

create_event_blueprint = Blueprint('create_event', __name__)

@create_event_blueprint.route('/create_event', methods = ['POST'])
def create_event():
    connection = create_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    event_date = request.form['event_date']
    event_name = request.form['event_name']
    event_discription = request.form['event_discription']
    event_type = request.form.get('event_type_selection')

    event_date = event_date.split('-')
    event_date = event_date[2] + '.' + event_date[1] + '.' + event_date[0]

    cursor.execute("""
                    insert into
                        evt.event
                    (event_id, event_date, event_name, discription, event_type_id)
                    values (default, %s, %s, %s, %s)""", (event_date, event_name, event_discription, event_type ))

    connection.commit() 
    cursor.close() 
    connection.close()

    return redirect(url_for('schedule_menu.schedule'))