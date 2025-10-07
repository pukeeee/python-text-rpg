import os
from dotenv import load_dotenv

# Завантажити змінні оточення
load_dotenv()

def run_application():
    """Перевіряє змінні оточення та запускає бота."""

    # Перевірка обов'язкових змінних оточення
    bot_token = os.getenv("BOT_TOKEN")
    database_url = os.getenv("DATABASE_URL")

    if not bot_token:
        print("❌ ПОМИЛКА: BOT_TOKEN не встановлено в .env файлі!")
        print("Створіть .env файл та додайте: BOT_TOKEN=your_bot_token_here")
        return

    if not database_url:
        print("❌ ПОМИЛКА: DATABASE_URL не встановлено в .env файлі!")
        print("Додайте в .env файл: DATABASE_URL=postgresql://user:password@host:port/dbname")
        return

    print("=" * 50)
    print("🎮 RPG Game - Telegram Bot is starting...")
    print("=" * 50)

    # Запуск бота
    from presentation.telegram.bot import main as start_bot_main
    start_bot_main()

if __name__ == "__main__":
    run_application()
