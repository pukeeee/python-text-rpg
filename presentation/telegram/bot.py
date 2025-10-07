import asyncio
import logging
import os
from aiogram import Bot, Dispatcher

from infrastructure.persistence.database import create_tables
from presentation.telegram.handlers import router

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Головна функція запуску бота"""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.critical("BOT_TOKEN не встановлено в змінних оточення!")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Реєструємо роутер з обробниками
    dp.include_router(router)

    logger.info("🚀 Запуск бота...")

    # Створюємо таблиці, якщо їх немає
    try:
        create_tables()
        logger.info("✅ База даних готова")
    except Exception as e:
        logger.error(f"❌ Помилка підключення до БД або створення таблиць: {e}")
        logger.error("Перевірте, чи запущено Docker контейнер з PostgreSQL та чи правильні налаштування в .env")
        return

    # Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
