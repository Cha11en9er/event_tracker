from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import psycopg2
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Настройка подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(host='localhost', database='your_db', user='your_user', password='your_password')
    return conn

# Функция для постоянного обновления данных
def update_data():
    while True:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, your_column FROM your_table')  # Получаем все необходимые данные
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        # Отправка обновленных данных на клиент
        data_to_send = [{'id': row[0], 'value': row[1]} for row in rows]
        socketio.emit('data_update', data_to_send)
        
        time.sleep(5)  # Интервал обновления данных (в секундах)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Запуск потока для обновления данных
    threading.Thread(target=update_data, daemon=True).start()
    socketio.run(app, debug=True)