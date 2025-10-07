"""
Головний файл для запуску Telegram-бота.
"""
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Імпортуємо роутер з обробниками
from presentation.telegram.handlers import router as handlers_router

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_bot():
    """
    Основна функція для налаштування та запуску бота.
    """
    # Ініціалізація бота
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN не встановлено в змінних оточення!")
        raise ValueError("BOT_TOKEN не встановлено!")

    bot = Bot(token=bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Реєстрація обробників з файлу handlers.py
    dp.include_router(handlers_router)

    logger.info("🚀 Запуск бота...")
    try:
        # Починаємо обробку оновлень
        await dp.start_polling(bot)
    finally:
        # Закриваємо сесію бота при зупинці
        await bot.session.close()

def main():
    """Точка входу для запуску бота."""
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Бот зупинено.")
    except ValueError as e:
        logger.critical(e)

# Цей блок не буде виконуватися при імпорті,
# але залишений для можливості прямого запуску файлу.
if __name__ == '__main__':
    main()
