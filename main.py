# main.py

import asyncio
import os
from dotenv import load_dotenv

# Завантажити змінні оточення
load_dotenv()

async def main():
    """Головна функція - запуск Telegram бота"""

    # Перевірка обов'язкових змінних оточення
    bot_token = os.getenv("BOT_TOKEN")
    database_url = os.getenv("DATABASE_URL")

    if not bot_token:
        print("❌ ПОМИЛКА: BOT_TOKEN не встановлено в .env файлі!")
        print("Створіть .env файл та додайте:")
        print("BOT_TOKEN=your_bot_token_here")
        return

    if not database_url:
        print("❌ ПОМИЛКА: DATABASE_URL не встановлено в .env файлі!")
        print("Додайте в .env файл:")
        print("DATABASE_URL=postgresql://rpg_user:password@localhost:5432/rpg_game")
        return

    print("🎮 RPG Game - Telegram Bot")
    print("=" * 50)

    # Запуск бота
    from presentation.telegram.bot import main as bot_main
    await bot_main()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот зупинено")
