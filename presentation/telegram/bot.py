import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import os

from infrastructure.persistence.database import get_session
from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository
from domain.services.stats_calculator import StatsCalculator
from application.use_cases.character import CreateCharacterUseCase, GetCharacterStatsUseCase
from application.dto.character_dto import CreateCharacterRequest, GetCharacterStatsRequest

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не встановлено в змінних оточення!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Зберігаємо стан створення персонажа
user_states = {}

# === Команди ===

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start - початок гри"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    # Перевіряємо чи є вже персонаж
    with get_session() as session:
        repo = PostgresCharacterRepository(session)
        existing = repo.get_by_telegram_user_id(user_id)

        if existing:
            await message.answer(
                f"🎮 Вітаю, {existing.name}!\n\n"
                f"Ваш персонаж вже створений.\n"
                f"Використовуйте /stats щоб побачити характеристики."
            )
            return

    # Якщо персонажа немає - просимо ввести ім'я
    user_states[user_id] = "awaiting_name"
    await message.answer(
        "🎮 Вітаємо в RPG!\n\n"
        "Введіть ім'я вашого персонажа (3-20 символів):"
    )

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Команда /stats - показати характеристики"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    try:
        with get_session() as session:
            repo = PostgresCharacterRepository(session)
            calculator = StatsCalculator()

            use_case = GetCharacterStatsUseCase(repo, calculator)
            request = GetCharacterStatsRequest(telegram_user_id=user_id)
            response = use_case.execute(request)

            stats = response.stats

            stats_text = (
                f"👤 **{response.name}** (Рівень {response.level})\n"
                f"📊 Досвід: {response.experience}/{response.experience_to_next_level}\n\n"

                f"❤️ Здоров'я: {stats.health}/{stats.max_health}\n"
                f"💙 Мана: {stats.mana}/{stats.max_mana}\n\n"

                f"⚔️ **Атака:**\n"
                f"• Урон: {stats.damage_min}-{stats.damage_max}\n"
                f"• Точність: {stats.accuracy}\n"
                f"• Крит. шанс: {stats.critical_chance:.1f}%\n"
                f"• Крит. множник: {stats.critical_multiplier:.1f}x\n"
                f"• Швидкість атаки: {stats.attack_speed:.2f}\n\n"

                f"🛡️ **Захист:**\n"
                f"• Броня: {stats.armor}\n"
                f"• Ухилення: {stats.evasion}\n"
                f"• Енерг. щит: {stats.energy_shield}\n\n"

                f"📈 **Характеристики:**\n"
                f"• Сила: {stats.strength}\n"
                f"• Спритність: {stats.dexterity}\n"
                f"• Інтелект: {stats.intelligence}\n\n"

                f"📍 Локація: {response.location}"
            )

            await message.answer(stats_text, parse_mode="Markdown")

    except ValueError:
        await message.answer(
            "❌ Персонаж не знайдений!\n"
            "Використовуйте /start щоб створити персонажа."
        )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help - допомога"""
    help_text = (
        "🎮 **Доступні команди:**\n\n"
        "/start - Почати гру / Створити персонажа\n"
        "/stats - Показати характеристики персонажа\n"
        "/help - Показати це повідомлення\n\n"
        "🚧 В розробці:\n"
        "• Дослідження локацій\n"
        "• Бойова система\n"
        "• Інвентар та екіпіровка"
    )

    await message.answer(help_text, parse_mode="Markdown")

# === Обробка створення персонажа ===

@dp.message()
async def handle_message(message: Message):
    """Обробка всіх інших повідомлень"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    # Якщо користувач у стані введення імені
    if user_states.get(user_id) == "awaiting_name":
        if not message.text:
            await message.answer("Будь ласка, введіть ім'я текстом.")
            return
        character_name = message.text.strip()

        try:
            with get_session() as session:
                repo = PostgresCharacterRepository(session)
                use_case = CreateCharacterUseCase(repo)

                request = CreateCharacterRequest(
                    telegram_user_id=user_id,
                    character_name=character_name
                )

                response = use_case.execute(request)
                session.commit()

                # Очищуємо стан
                user_states.pop(user_id, None)

                await message.answer(
                    f"✅ {response.message}\n\n"
                    f"🎉 Рівень: {response.level}\n"
                    f"📊 Використовуйте /stats щоб побачити характеристики"
                )

        except ValueError as e:
            await message.answer(f"❌ Помилка: {str(e)}")
    else:
        await message.answer(
            "Використовуйте /start щоб почати гру або /help для допомоги"
        )

# === Запуск бота ===

async def main():
    """Головна функція запуску бота"""
    logger.info("🚀 Запуск бота...")

    # Створюємо таблиці якщо їх немає
    from infrastructure.persistence.database import create_tables
    create_tables()
    logger.info("✅ База даних готова")

    # Запускаємо бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
