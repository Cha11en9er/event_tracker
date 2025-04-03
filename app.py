import sys
import os

# Добавляем пути к модулям
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "event_tracker.webui")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "event_tracker.webui/src")))

# Создаем простое Flask-приложение для тестирования
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Event Tracker!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082) 