from flask import Blueprint, render_template, session
import psycopg2, psycopg2.extras

report_general_event_statistics_blueprint = Blueprint('report_general_event_statistics', __name__)

@report_general_event_statistics_blueprint.route('/reports/general-statistics')
def report_general_event_statistics_page():
    user_data = session['id']
    connection = report_general_event_statistics_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
                    SELECT json_agg(n)
                    FROM (
                        SELECT 
                            count(e.event_id),
                            et.event_type_name
                        FROM evt."event" AS e
                        LEFT JOIN evt.event_type AS et
                        ON e.event_type_id = et.event_type_id
                        WHERE et.event_type_name <> 'собрание'
                        GROUP BY et.event_type_name
                    ) n;
                   """)
    event_statistics_data = cursor.fetchone()[0]

    # готовый запрос
    # cursor.execute("""
    #                 SELECT json_build_object(
    #                     'data', (
    #                         SELECT json_agg(row_to_json(t))
    #                         FROM (
    #                             SELECT 
    #                                 count(e.event_id) AS count,
    #                                 et.event_type_name
    #                             FROM evt."event" e
    #                             LEFT JOIN evt.event_type et ON e.event_type_id = et.event_type_id
    #                             GROUP BY et.event_type_name
    #                         ) t
    #                     ),
    #                     'base_event_type_name', (
    #                         SELECT array_agg(DISTINCT et.event_type_name)
    #                         FROM evt.event_type et
    #                     )
    #                 ) AS result;
    #                """)
    # data = cursor.fetchone()[0]
    # participant_data = data['data']
    # base_event_type_name = data['base_event_type_name']
    # user_data = session['id']

    print(user_data)
    return render_template('report_general_event_statistics.html',
                           user_data=user_data,
                           event_statistics_data=event_statistics_data)
