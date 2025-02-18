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
                            r.role_discription
                          FROM evt.user as u 
                          INNER JOIN evt.role AS r
                          ON u.user_id = r.user_id
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
        if account_register: # проверка на наличие аккаунта
            flash('Такой аккаунт сущесвтует, войдите в него')
        elif len(fullname) == 0: # првоерка на наличие имени
            flash('Введите своё имя')
        elif len(username) == 0: # првоерка на наличие логина
            flash('Введите свой логин')
        elif len(password) == 0: # првоерка на наличие пароля
            flash('Введите свой пароль')
        elif len(email) == 0: # првоерка на наличие почты
            flash('Введите свою почу')
        else:
            cursor.execute("INSERT INTO evt.user (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            connection.commit()
            flash('Вы зарегестрировались!')

            cursor.execute('SELECT * FROM evt.user WHERE username = %s', (username,))
            account_data = cursor.fetchone()

            cursor.execute("INSERT INTO evt.role (user_id, role_discription) VALUES (%s, %s)", (account_data[0], 'Viewer'))
            connection.commit()

            cursor.execute('SELECT role_discription FROM evt.role WHERE user_id = %s', (account_data[0],))
            role_data = cursor.fetchone()

            session['loggedin'] = True
            session['id'] = account_data[0]
            session['username'] = account_data[2]
            session['fullname'] = account_data[1]
            session['role'] = role_data[0]

            return redirect(url_for('schedule_menu.schedule'))

    return render_template('register.html')

@auth_blueprint.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('auth.main'))