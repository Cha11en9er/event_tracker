import sys
import os

# Добавляем пути к модулям
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "event_tracker_webui")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "event_tracker_webui/src")))

# Импортируем функцию create_app из модуля website
try:
    from event_tracker_webui.src.website import create_app
except ImportError:
    try:
        from website import create_app
    except ImportError:
        from flask import Flask
        
        # Если не удается импортировать, создаем базовое приложение
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Hello, Event Tracker!"
        
        @app.route('/health')
        def health():
            return "OK", 200
    else:
        # Создаем экземпляр приложения из website
        app = create_app()
else:
    # Создаем экземпляр приложения из event_tracker_webui.src.website
    app = create_app()

# Добавляем эндпоинт здоровья, если его нет
if not any(rule.endpoint == 'health' for rule in app.url_map.iter_rules()):
    @app.route('/health')
    def health_check():
        return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082) 