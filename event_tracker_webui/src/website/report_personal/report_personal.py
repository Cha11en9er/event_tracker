from flask import Blueprint, render_template, session, request, jsonify
import psycopg2, psycopg2.extras
from datetime import datetime, timedelta
import logging

report_personal_blueprint = Blueprint('report_personal', __name__)

@report_personal_blueprint.route('/reports/report-personal')
def report_personal_page():

    connection = report_personal_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get event participation data
    cursor.execute("""
                    WITH dates AS (
                        SELECT generate_series(
                            '2025-05-01'::date,
                            '2025-05-31'::date,
                            '1 day'::interval
                        )::date as visit_date
                    )
                    SELECT json_build_object(
                        'data_person_visits_to_date', (
                            SELECT json_agg(row_to_json(t))
                            FROM (
                                SELECT
                                    d.visit_date AS event_date,
                                    COUNT(e.event_id) AS event_participant
                                FROM dates d
                                LEFT JOIN evt.event e ON DATE(e.event_date) = d.visit_date
                                LEFT JOIN evt.event_participation ep ON e.event_id = ep.event_id
                                LEFT JOIN evt."user" u ON ep.user_id = u.user_id
                                GROUP BY
                                    d.visit_date
                                ORDER BY
                                    d.visit_date
                            ) t
                        )
                    ) AS result;              
                    """)
    
    data = cursor.fetchone()[0]
    data_person_visits_to_date = data['data_person_visits_to_date']

    # Get participant data
    cursor.execute("""
        SELECT 
            u.user_id,
            u.fullname,
            COUNT(ep.event_id) as event_participant
        FROM evt."user" u
        LEFT JOIN evt.event_participation ep ON u.user_id = ep.user_id
        GROUP BY u.user_id, u.fullname
        ORDER BY event_participant DESC
    """)
    
    participant_data = cursor.fetchall()
    user_data = session['id']

    return render_template('report_personal.html',
                           user_data=user_data,
                           data_person_visits_to_date=data_person_visits_to_date,
                           participant_data=participant_data)


