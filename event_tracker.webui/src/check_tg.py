import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,  # Новый способ создания Updater
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import os
from dotenv import load_dotenv
import psycopg2
load_dotenv()

def db_connection():
    env_host = os.getenv('DB_HOST')
    env_port = os.getenv('DB_PORT')
    env_database = os.getenv('DB_NAME')
    env_user = os.getenv('DB_USER')
    env_password = os.getenv('DB_PASSWORD')
    connection = psycopg2.connect(host=env_host, port=env_port, database=env_database, user=env_user, password=env_password) 
    return connection

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TG_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    connection = db_connection()
    cursor = connection.cursor()
    user = update.effective_user
    await update.message.reply_text(f"Привет, {user.first_name}! Бот работает. Здесь будут оповещения о событиях")
    chat_id = update.effective_chat.id
    try:
        cursor.execute("""
            INSERT INTO evt.subscribe (chat_id)
            VALUES (%s)
        """, (chat_id,))
        connection.commit()
        print(f"{chat_id} был добавлен")
    except Exception as e:
        print(f"Ошибка при вставке id")
    finally:
        cursor.close()
        connection.close()
    # print(f"ID чата: {chat_id}")

def main() -> None:
    # Создаем Application вместо Updater
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()