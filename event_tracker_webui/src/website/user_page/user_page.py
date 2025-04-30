from flask import Blueprint, render_template, session, jsonify, request
import json
import psycopg2, psycopg2.extras
import requests
import os
from dotenv import load_dotenv

load_dotenv()

user_page_blueprint = Blueprint('user_page', __name__)

@user_page_blueprint.route('/user_page/<int:user_id_from_form>', methods = ['GET', 'POST'])
def user_page(user_id_from_form):
    connection = user_page_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        
        cursor.execute("""
                        SELECT 
                            json_build_object(
                            'user_fullname', u.fullname,
                            'user_name', u.username,
                            'user_id', u.user_id,
                            'user_email', u.email,
                            'telegram_id', u.telegram_id,
                            'user_participation', array_agg(
                                json_build_object(
                                'event_name', e.event_name,
                                'event_id', e.event_id,
                                'user_event_role', r.role_name)) 
                            ) AS DATA
                            FROM evt."user" as u
                            LEFT JOIN evt.event_participation AS ep 
                            ON u.user_id = ep.user_id
                            LEFT JOIN evt."event" AS e
                            ON ep.event_id = e.event_id
                            LEFT JOIN evt.ROLE AS r
                            ON ep.user_event_role_id = r.role_id
                            WHERE u.user_id = %s
                            GROUP BY 
                                u.fullname,
                                u.username,
                                u.email,
                                u.telegram_id,
                                u.user_id;
                        """ % user_id_from_form)
        user_data = cursor.fetchone()[0]

        user_data['session_user_id'] = session['id']

        print(user_data)    
    return render_template('user_page.html', user_data = user_data)