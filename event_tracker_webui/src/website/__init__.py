from flask import Flask
from dotenv import load_dotenv
import os
import psycopg2, psycopg2.extras

from .auth.auth import auth_blueprint
from .schedule_menu.schedule_menu import schedule_menu_blueprint
from .current_event.current_event import current_event_blueprint
from .sub_unsub_event.sub_unsub_event import sub_unsub_event_blueprint
from .create_event.create_event import create_event_blueprint
from .user_page.user_page import user_page_blueprint
from .delete_event.delete_event import delete_event_blueprint
from .search_event.search_event import search_event_blueprint
from .edit_profile.edit_profile import edit_profile_blueprint
from .send_notif.send_notif import send_notif_blueprint

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

    # Список всех blueprint'ов
    blueprints = [
        auth_blueprint,
        schedule_menu_blueprint,
        current_event_blueprint,
        sub_unsub_event_blueprint,
        create_event_blueprint,
        user_page_blueprint,
        delete_event_blueprint,
        search_event_blueprint,
        edit_profile_blueprint,
        send_notif_blueprint
    ]

    # Регистрация всех blueprint'ов и назначение функции подключения к БД
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/')
        blueprint.db_connection = db_connection

    return app