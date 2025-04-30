from flask import render_template, redirect, Blueprint, request, url_for, session, flash
import psycopg2, psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/')
def main():
    return render_template('main.html')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    connection = auth_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('''SELECT 
                            u.user_id,
                            u.fullname,
                            u.username,
                            u.password,
                            r.role_name,
                            u.telegram_id
                          FROM evt.user as u 
                          INNER JOIN evt.role AS r
                          ON u.user_role_id = r.role_id
                          WHERE username = %s''', (username,))
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[2]
                session['fullname'] = account[1]
                session['role'] = account[4]
                session['telegram_id'] = account[5]
                flash('Вы вошли в систему!')
                return redirect(url_for('schedule_menu.schedule'))
            else:
                flash('Неверный логин или пароль')
        else:
            flash('Неверный логин или пароль')
    
    return render_template('login.html')

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    connection = auth_blueprint.db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        cursor.execute('SELECT * FROM evt.user WHERE username = %s', (username,))
        account_register = cursor.fetchone()
        if account_register:
            flash('Такой аккаунт существует, войдите в него')
        elif len(fullname) == 0:
            flash('Введите своё имя')
        elif len(username) == 0:
            flash('Введите свой логин')
        elif len(password) == 0:
            flash('Введите свой пароль')
        elif len(email) == 0:
            flash('Введите свою почту')
        else:
            # Создаем пользователя и получаем его данные через RETURNING
            cursor.execute("""
                INSERT INTO evt.user 
                    (fullname, username, password, email, user_role_id) 
                VALUES 
                    (%s, %s, %s, %s, 2)
                RETURNING 
                    user_id, 
                    fullname, 
                    username,
                    telegram_id
                """, (fullname, username, _hashed_password, email))
            
            user_data = cursor.fetchone()

            # Получаем название роли через JOIN
            cursor.execute("""
                SELECT r.role_name 
                FROM evt.role AS r 
                INNER JOIN evt.user AS u
                ON %s = r.role_id
            """, (user_data['user_id'],))
            role_data = cursor.fetchone()

            connection.commit()
            flash('Вы зарегистрировались!')

            # Устанавливаем данные сессии
            session['loggedin'] = True
            session['id'] = user_data['user_id']
            session['username'] = user_data['username']
            session['fullname'] = user_data['fullname']
            session['role'] = role_data['role_name']
            session['telegram_id'] = user_data['telegram_id']

            return redirect(url_for('schedule_menu.schedule'))

    return render_template('register.html')

@auth_blueprint.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('auth.main'))