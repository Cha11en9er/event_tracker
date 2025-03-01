from flask import request, Blueprint, jsonify, session
import psycopg2, psycopg2.extras

edit_profile_blueprint = Blueprint('edit_profile', __name__)

@edit_profile_blueprint.route('/edit_profile', methods=['POST'])
def edit_profile():
    data_from_js=request.get_json()
    
    connection=edit_profile_blueprint.db_connection()
    cursor=connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    user_fullname=data_from_js['fullname']
    user_email=data_from_js['email']
    user_telegram_id=data_from_js['telegram_id']
    user_password=data_from_js['password']
    user_id=data_from_js['user_id']

    cursor.execute("""
                    UPDATE evt.user
                    SET fullname = %s,
                        email = %s,
                        telegram_id = %s,
                        sys_changed_at = CURRENT_TIMESTAMP(0)::timestamp without time zone,
                        sys_changed_by = %s
                    WHERE user_id = %s;
                    """, (user_fullname, user_email, user_telegram_id, user_id, user_id))

    connection.commit() 
    
    cursor.execute("SELECT fullname, email, telegram_id FROM evt.user WHERE user_id = %s", (user_id,))
    updated_user_data = cursor.fetchone()

    session['fullname'] = updated_user_data[0]
    session['telegram_id'] = updated_user_data[2]

    cursor.close()
    connection.close()

    return jsonify({
        'fullname': updated_user_data['fullname'],
        'email': updated_user_data['email'],
        'telegram_id': updated_user_data['telegram_id']
    })
