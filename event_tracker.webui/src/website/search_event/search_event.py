from flask import request, redirect, url_for, Blueprint
import psycopg2, psycopg2.extras

search_event_blueprint = Blueprint('search_event', __name__)

@search_event_blueprint.route('/search_event', methods = ['POST'])
def search_event():
    connection = search_event_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory = psycopg2.extras.DictCursor)

    search_info = request.form['search_info']

    print(search_info)