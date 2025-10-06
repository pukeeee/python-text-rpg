# tests/infrastructure/persistence/test_postgres_character_repository.py
"""
Інтеграційні тести для PostgresCharacterRepository.
"""
from uuid import uuid4

from domain.entities.character import Character
from domain.value_objects.stats import BaseStats
from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository


class TestPostgresCharacterRepository:
    """Групує тести для репозиторію персонажів."""

    def test_save_and_get_character(self, db_session):
        """Перевіряє базовий функціонал збереження та отримання персонажа."""
        # 1. Підготовка даних
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        base_stats = BaseStats(strength=12, dexterity=14, intelligence=10, base_health=110, base_mana=55)

        original_character = Character(
            id=character_id,
            telegram_user_id=12345,
            name="Test_Hero",
            level=5,
            experience=1500,
            base_stats=base_stats,
            current_health=100,
            current_mana=50,
            location_id="test_location",
            equipped_items={'weapon': 'sword_1'},
            inventory=['potion_1', 'potion_1']
        )

        # 2. Дія: Зберігаємо персонажа
        repo.save(original_character)
        db_session.commit() # Потрібен коміт, щоб дані збереглися в транзакції

        # 3. Перевірка: Отримуємо персонажа з БД
        retrieved_character = repo.get(character_id)

        # 4. Твердження: Перевіряємо, що отримані дані відповідають оригіналу
        assert retrieved_character is not None
        assert retrieved_character.id == original_character.id
        assert retrieved_character.name == "Test_Hero"
        assert retrieved_character.level == 5
        assert retrieved_character.telegram_user_id == 12345
        assert retrieved_character.base_stats.strength == 12
        assert retrieved_character.current_health == 100
        assert retrieved_character.location_id == "test_location"
        assert retrieved_character.equipped_items.get('weapon') == 'sword_1'
        assert 'potion_1' in retrieved_character.inventory
        assert retrieved_character.inventory.count('potion_1') == 2
