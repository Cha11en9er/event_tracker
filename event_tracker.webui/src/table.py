from flask import Flask, jsonify, render_template
import psycopg2

app = Flask(__name__)

# Настройка подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(database="EventTrackerDB", user="postgres", password="OORCra23ppo)", host="localhost", port="5432") 
    return conn

@app.route('/')
def index():
    return render_template('table.html')

@app.route('/get_data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
                        select
                            e.event_date,
                            e.event_name,
                            e.discription,
                            count(ep.event_participation_id)
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
                            e.event_date''')  # Замените на ваши столбцы и таблицу
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Преобразование данных в список словарей
    data = [{'id': row[0], 'column1': row[1], 'column2': row[2], 'column3': row[3]} for row in rows]
    return jsonify(data)  # Возвращаем данные в формате JSON

if __name__ == '__main__':
    app.run(debug=True)