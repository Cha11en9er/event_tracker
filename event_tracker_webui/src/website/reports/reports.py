from flask import Blueprint, render_template, session

reports_blueprint = Blueprint('reports', __name__)

@reports_blueprint.route('/reports')
def reports_page():
    user_data = session['id']
    return render_template('reports.html', user_data=user_data)
