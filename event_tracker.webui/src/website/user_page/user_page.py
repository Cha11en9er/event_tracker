from flask import Blueprint
import psycopg2, psycopg2.extras

user_page_blueprint = Blueprint('user_page', __name__)

@user_page_blueprint.route('/user_page/<int:user_id_from_form>', methods = ['GET', 'POST'])
def user_page(user_id_from_form):
    connection = user_page_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)