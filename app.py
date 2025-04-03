import sys
import os

# Добавляем текущий каталог в путь поиска модулей
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Импортируем функцию create_app из website
from website import create_app

# Создаем экземпляр приложения
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082) 