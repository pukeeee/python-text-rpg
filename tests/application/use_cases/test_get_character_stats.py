import pytest

from application.use_cases.character import GetCharacterStatsUseCase
from application.dto.character_dto import GetCharacterStatsRequest
from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository
from infrastructure.persistence.repositories.json_item_repository import JsonItemRepository
from domain.services.stats_calculator import StatsCalculator
from domain.entities.character import Character
from domain.value_objects.stats import BaseStats

class TestGetCharacterStatsUseCase:
    """Тести для GetCharacterStatsUseCase"""

    def test_get_stats_success(self, db_session):
        """Тест успішного отримання характеристик"""
        # Arrange - створюємо персонажа
        repo = PostgresCharacterRepository(db_session)
        item_repo = JsonItemRepository(data_path="data")
        calculator = StatsCalculator(item_repository=item_repo)

        character = Character(
            telegram_user_id=56789,
            name="StatsTestHero",
            base_stats=BaseStats(15, 20, 12, 120, 60),
            level=5,
            experience=500
        )
        repo.save(character)
        db_session.commit()

        # Act
        use_case = GetCharacterStatsUseCase(repo, calculator)
        request = GetCharacterStatsRequest(telegram_user_id=56789)
        response = use_case.execute(request)

        # Assert
        assert response.name == "StatsTestHero"
        assert response.level == 5
        assert response.experience == 500
        assert response.stats.strength == 15
        assert response.stats.dexterity == 20
        assert response.stats.intelligence == 12
        # Перевіряємо розраховані характеристики
        assert response.stats.max_health == 120 + (15 * 5)  # base_health + strength * 5
        assert response.stats.damage_min > 0
        assert response.stats.damage_max > response.stats.damage_min

    def test_get_stats_character_not_found(self, db_session):
        """Тест коли персонаж не знайдений"""
        repo = PostgresCharacterRepository(db_session)
        item_repo = JsonItemRepository(data_path="data")
        calculator = StatsCalculator(item_repository=item_repo)

        use_case = GetCharacterStatsUseCase(repo, calculator)
        request = GetCharacterStatsRequest(telegram_user_id=99999)

        with pytest.raises(ValueError, match="не знайдений"):
            use_case.execute(request)
