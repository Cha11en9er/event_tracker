from flask import render_template, Blueprint, session, request
import psycopg2, psycopg2.extras
import re

current_event_blueprint = Blueprint('current_event', __name__)

@current_event_blueprint.route('/current_event/<int:event_id_from_form>', methods = ['GET', 'POST'])
def current_event(event_id_from_form):
    connection = current_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def add_hyperlinks(text):
        url_pattern = re.compile(r'(https?://\S+)')

        def replace_with_link(match):
            url = match.group(0)
            return f"<a href='{url}' target='_blank' rel='noopener noreferrer'>{url}</a>"

        return url_pattern.sub(replace_with_link, text)

    event_date = request.args.get('date')
    event_name = request.args.get('name')
    event_disc = request.args.get('disc')   
    event_time = request.args.get('time')

    event_disc = add_hyperlinks(event_disc)

    cursor.execute('''
                select
                    u.fullname,
                    u.user_id
                from
                    evt.event as e
                left join evt.event_participation as ep on
                    e.event_id = ep.event_id
                left join evt.user as u on
                    ep.user_id = u.user_id 
                where 
                   e.event_id = %s ''', (event_id_from_form,))
    participant_data = cursor.fetchall()

    username = session['username']
    role = session['role']
    event_id = event_id_from_form

    user_data = {"username": username, "event_name": event_name, "event_date": event_date, "user_role" : role, "event_id" : event_id, "event_disc": event_disc, "event_time": event_time, "user_telegram_id": session["telegram_id"], "user_id": session["id"]}

    if not participant_data or (len(participant_data) == 1 and participant_data[0] == [None, None]):
        participant_data = [['Здесь пока нету участников. Вы можете стать первым']]
        # return render_template('current_event.html', data = participant_data, static_data = user_data)
    
    return render_template('current_event.html', data = participant_data, static_data = user_data)