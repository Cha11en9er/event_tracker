from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from flask_socketio import SocketIO, emit
import psycopg2, psycopg2.extras
import json 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '**'
db_password = '**'
db_host = "**"
db_port = "**"

def db_connection():
    connection = psycopg2.connect(database="EventTrackerDB", user="postgres", password = db_password, host = db_host, port = db_port) 
    return connection


@app.route('/')
def main():
    return render_template('main.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        print(fullname, username, password, email)

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
            session['loggedin'] = True
            session['id'] = account_data[0]
            session['username'] = account_data[2]
            
            return redirect(url_for('schedule'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM evt.user WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[2]
                return redirect(url_for('schedule'))
            else:
                flash('Неверный логин или пароль')
        else:
            flash('Неверный логин или пароль')

    return render_template('login.html')

# @app.route('/schedule', methods=['GET', 'POST'])
# def schedule():

#     cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

#     if 'loggedin' in session:
#         cursor.execute('SELECT * FROM evt.user WHERE user_id = %s', [session['id']])
#         account = cursor.fetchone()

#         cursor.execute('''
#                         select
#                             e.event_date,
#                             e.event_name,
#                             e.discription,
#                             et.event_type_name,
#                             count(ep.event_participation_id),
#                             e.event_id
#                         from
#                             evt.event as e
#                         inner join evt.event_type as et on
#                             e.event_type_id = et.event_type_id
#                         left join evt.event_participation ep on
#                             e.event_id = ep.event_id
#                         group by 
#                             e.event_id,
#                             et.event_type_name
#                         order by
#                             e.event_date''')
#         data = cursor.fetchall()

#         return render_template('schedule.html', account = account, data = data)

#     return redirect(url_for('login'))

@app.route('/schedule')
def schedule():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        cursor.execute('SELECT * FROM evt.user WHERE user_id = %s', [session['id']])
        account = cursor.fetchone()
        return render_template('schedule.html', account = account)

@app.route('/get_schedule_data', methods = ['GET'])
def get_schedule_data():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('''
                        select
                            e.event_date,
                            e.event_name,
                            e.discription,
                            et.event_type_name,
                            count(ep.event_participation_id),
                            e.event_id
                        from
                            evt.event as e
                        inner join evt.event_type as et on
                            e.event_type_id = et.event_type_id
                        left join evt.event_participation ep on
                            e.event_id = ep.event_id
                        group by
                            e.event_id,
                            et.event_type_name
                        order by
                            e.event_date''')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    data = [{'event_date': row[0], 'event_name': row[1], 'event_disc': row[2], 'event_type': row[3], 'participation_count': row[4], 'event_id': row[5], 'user_id': session['id']} for row in rows]
    return jsonify(data)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('main'))

@app.route('/create_event', methods = ['POST'])
def create_event():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    event_date = request.form['event_date']
    event_name = request.form['event_name']
    event_discription = request.form['event_discription']
    event_count = 0
    cursor.execute('''INSERT INTO evt.event (event_date, event_name, discription) VALUES (%s, %s, %s)''', (event_date, event_name, event_discription)) 

    connection.commit() 
    cursor.close() 
    connection.close()

    return redirect(url_for('schedule'))

@app.route('/current_event/<int:event_id_from_form>', methods = ['GET', 'POST'])
def current_event(event_id_from_form):
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute(''' 
                select
                    e.event_date,
                    e.event_name,
                    u.fullname
                from
                    evt.event as e
                inner join evt.event_participation as ep on
                    e.event_id = ep.event_id
                inner join evt.user as u on
                    ep.user_id = u.user_id 
                where 
                   e.event_id = %s ''', (event_id_from_form, ))
    data = cursor.fetchall()
    
    username = session['username']

    return render_template('current_event.html', data = data, username = username)

@app.route('/subscribe_to_event', methods = ['POST'])
def subscribe_to_event():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    event_id = request.form.get('event_id_from_js')
    user_id = request.form.get('user_id_from_js')
    participation_status = 'subscribed'

    cursor.execute('''
                    insert into
                        evt.event_participation as ep 
                    (event_id, user_id, participation_status)
                    values(%s, %s, %s)''', (event_id, user_id, participation_status, ))
    connection.commit() 
    cursor.close() 
    connection.close()

    return redirect(url_for('schedule'))

@app.route('/unsubscribe_from_event', methods = ['POST'])
def unsubscribe_from_event():
    connection = db_connection()
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    event_id = request.form.get('event_id_from_js')
    user_id = request.form.get('user_id_from_js')

    cursor.execute('''
                    delete from 
                        evt.event_participation
                    where
                        event_id = %s
                    and 
                        user_id = %s''',
                    (event_id, user_id, ))
    connection.commit() 
    cursor.close() 
    connection.close()

    return redirect(url_for('schedule'))

if __name__ == '__main__':
    app.run(debug = True)