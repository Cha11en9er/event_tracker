from flask import Blueprint, render_template, session, request, jsonify
import psycopg2, psycopg2.extras
from datetime import datetime, timedelta
import logging

report_personal_blueprint = Blueprint('report_personal', __name__)

@report_personal_blueprint.route('/reports/report-personal')
def report_personal_page():

    connection = report_personal_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
                                WHERE 
                                    u.username = 'username_участника'
                                    OR u.username IS NULL
                                GROUP BY
                                    d.visit_date
                                ORDER BY
                                    d.visit_date
                            ) t
                        )
                    ) AS result;                  
                    """)
    
    data = cursor.fetchone()[0]
    print(data)
    user_data = session['id']

    return render_template('report_personal.html', user_data=user_data)


