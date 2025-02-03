from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
import psycopg2, psycopg2.extras

from auth.auth import auth_blueprint
from schedule_menu.schedule_menu import schedule_menu_blueprint, schedule_socket
from current_event.current_event import current_event_blueprint
from sub_unsub_event.sub_unsub_event import sub_unsub_event_blueprint
from create_event.create_event import create_event_blueprint
from user_page.user_page import user_page_blueprint

load_dotenv()

def db_connection():
    env_host = os.getenv('DB_HOST')
    env_port = os.getenv('DB_PORT')
    env_database = os.getenv('DB_NAME')
    env_user = os.getenv('DB_USER')
    env_password = os.getenv('DB_PASSWORD')
    connection = psycopg2.connect(host=env_host, port=env_port, database=env_database, user=env_user, password=env_password) 
    return connection

def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv('SECRET_KEY')

    app.register_blueprint(auth_blueprint, url_prefix='/')
    app.register_blueprint(schedule_menu_blueprint, url_prefix='/')
    app.register_blueprint(current_event_blueprint, url_prefix='/')
    app.register_blueprint(sub_unsub_event_blueprint, url_prefix='/')
    app.register_blueprint(create_event_blueprint, url_prefix='/')
    app.register_blueprint(user_page_blueprint, url_prefix='/')


    auth_blueprint.db_connection = db_connection
    schedule_menu_blueprint.db_connection = db_connection
    current_event_blueprint.db_connection = db_connection
    sub_unsub_event_blueprint.db_connection = db_connection
    create_event_blueprint.db_connection = db_connection
    user_page_blueprint.db_connection = db_connection

    # Initialize the SocketIO instance with the Flask app
    socketio_app = SocketIO(app)

    return app, socketio_app

# Create the app and socketio_app
app, socketio_app = create_app()

# Register the socket event handlers
schedule_socket(socketio_app)

if __name__ == '__main__':
    # Run the socketio_app with the Flask app
    socketio_app.run(app, debug=True)
