from flask import Blueprint, render_template, session, request, jsonify
import psycopg2, psycopg2.extras
from datetime import datetime, timedelta
import logging

report_participant_blueprint = Blueprint('report_participant', __name__)

def get_period_display(period_type, **kwargs):
    if period_type == 'date':
        date_from = kwargs.get('dateFrom')
        date_to = kwargs.get('dateTo')
        if date_from and date_to:
            return f"с {date_from} по {date_to}"
        return "за последние 10 дней"
    elif period_type == 'week':
        week = kwargs.get('week')
        if week:
            today = datetime.now()
            first_day = today.replace(day=1)
            week_start = first_day + timedelta(days=(int(week)-1)*7)
            week_end = week_start + timedelta(days=6)
            return f"за {week}-ю неделю ({week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')})"
    elif period_type == 'month':
        month = kwargs.get('month')
        if month:
            months = {
                '1': 'январь', '2': 'февраль', '3': 'март', '4': 'апрель',
                '5': 'май', '6': 'июнь', '7': 'июль', '8': 'август',
                '9': 'сентябрь', '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'
            }
            return f"за {months[month]}"
    elif period_type == 'quarter':
        quarter = kwargs.get('quarter')
        if quarter:
            return f"за {quarter}-й квартал"
    elif period_type == 'year':
        year = kwargs.get('year')
        if year:
            return f"за {year} год"
    return "за последние 10 дней"

@report_participant_blueprint.route('/reports/report-participant')
def report_participant_page():
    try:
        connection = report_participant_blueprint.db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Get filter parameters from request
        period_type = request.args.get('periodType', 'date')
        event_type = request.args.get('eventType', 'all')
        
        # Build WHERE clause based on filters
        where_clause = "WHERE 1=1"
        
        if period_type == 'date':
            date_from = request.args.get('dateFrom')
            date_to = request.args.get('dateTo')
            if date_from and date_to:
                where_clause += f" AND e.event_date >= '{date_from}' AND e.event_date <= '{date_to}'"
        elif period_type == 'week':
            week = request.args.get('week')
            if week:
                # Calculate date range for the selected week
                today = datetime.now()
                first_day = today.replace(day=1)
                week_start = first_day + timedelta(days=(int(week)-1)*7)
                week_end = week_start + timedelta(days=6)
                where_clause += f" AND e.event_date >= '{week_start.date()}' AND e.event_date <= '{week_end.date()}'"
        elif period_type == 'month':
            month = request.args.get('month')
            if month:
                where_clause += f" AND EXTRACT(MONTH FROM e.event_date) = {month}"
        elif period_type == 'quarter':
            quarter = request.args.get('quarter')
            if quarter:
                where_clause += f" AND EXTRACT(QUARTER FROM e.event_date) = {quarter}"
        elif period_type == 'year':
            year = request.args.get('year')
            if year:
                where_clause += f" AND EXTRACT(YEAR FROM e.event_date) = {year}"
        
        # If no filters are applied, show last 10 days by default
        if period_type == 'date' and not request.args.get('dateFrom'):
            where_clause += f" AND e.event_date > now() - INTERVAL '10 days' AND e.event_date <= now()"
        
        # Add event type filter if specified
        if event_type != 'all':
            where_clause += f" AND e.event_type_id IN (SELECT event_type_id FROM evt.event_type WHERE event_type_name = '{event_type}')"

        query = f"""
                    SELECT json_build_object(
                        'participant_data', (
                            SELECT json_agg(row_to_json(t))
                            FROM (
                                SELECT 
                                    count(ep.user_id) AS count,
                                    u.fullname
                                FROM evt.event_participation AS ep
                                LEFT JOIN evt."user" AS u ON ep.user_id = u.user_id
                                LEFT JOIN evt."event" AS e ON ep.event_id = e.event_id
                                {where_clause}
                                GROUP BY u.fullname
                                ORDER BY count(ep.user_id) DESC
                                LIMIT 10
                            ) t
                        ),
                        'base_event_type_name', (
                            SELECT array_agg(DISTINCT et.event_type_name)
                            FROM evt.event_type et
                        )
                    ) AS result;
                   """
        
        cursor.execute(query)
        data = cursor.fetchone()[0]
        
        if not data:
            return jsonify({'error': 'No data found'}), 404
            
        participant_data = data['participant_data']
        base_event_type_name = data['base_event_type_name']
        user_data = session['id']

        # Get period display text
        period_display = get_period_display(
            period_type,
            dateFrom=request.args.get('dateFrom'),
            dateTo=request.args.get('dateTo'),
            week=request.args.get('week'),
            month=request.args.get('month'),
            quarter=request.args.get('quarter'),
            year=request.args.get('year')
        )
        
        # Add period display to data
        data['period_display'] = period_display
        
        # If it's an AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(data)
        
        # Otherwise return the full HTML page
        return render_template('report_participant.html', 
                             user_data=user_data,
                             participant_data=participant_data,
                             base_event_type_name=base_event_type_name,
                             period_display=period_display)
                             
    except Exception as e:
        logging.error(f"Error in report_participant_page: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('error.html', error=str(e)), 500

