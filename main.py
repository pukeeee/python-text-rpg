import asyncio
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

async def main():
    """Главная функция приложения"""
    print("🎮 RPG Game starting...")

    # Для MVP - простой CLI
    # Позже заменим на Telegram бота

    from infrastructure.persistence.database import create_tables, get_session
    from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository
    from domain.value_objects.stats import BaseStats
    from domain.entities.character import Character
    from domain.services.stats_calculator import StatsCalculator

    # Создание таблиц если их нет
    create_tables()
    print("✅ Database tables ready")

    # Простое демо для проверки
    with get_session() as session:
        repo = PostgresCharacterRepository(session)
        calculator = StatsCalculator()

        # Создание тестового персонажа
        test_char = Character(
            telegram_user_id=1,
            name="Test Hero",
            base_stats=BaseStats(
                strength=10,
                dexterity=10,
                intelligence=10,
                base_health=100,
                base_mana=50
            )
        )

        # Сохранение
        repo.save(test_char)
        session.commit()
        print(f"✅ Created character: {test_char.name}")

        # Загрузка
        loaded = repo.get(test_char.id)
        if loaded:
            print(f"✅ Loaded character: {loaded.name}")

            # Расчёт характеристик
            stats = calculator.calculate_total_stats(loaded)
            print("✅ Character stats calculated:")
            print(f"   Health: {stats.health}/{stats.max_health}")
            print(f"   Damage: {stats.damage_min}-{stats.damage_max}")
            print(f"   Armor: {stats.armor}, Evasion: {stats.evasion}")
        else:
            print("❌ Помилка: не вдалося завантажити персонажа.")

    print("🎉 All systems operational!")

if __name__ == "__main__":
    asyncio.run(main())
