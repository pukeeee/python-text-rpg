import pytest

from application.use_cases.character import CreateCharacterUseCase
from application.dto.character_dto import CreateCharacterRequest
from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository

class TestCreateCharacterUseCase:
    """Тести для CreateCharacterUseCase"""

    def test_create_character_success(self, db_session):
        """Тест успішного створення персонажа"""
        # Arrange
        repo = PostgresCharacterRepository(db_session)
        use_case = CreateCharacterUseCase(repo)
        request = CreateCharacterRequest(
            telegram_user_id=12345,
            character_name="TestHero"
        )

        # Act
        response = use_case.execute(request)
        db_session.commit()

        # Assert
        assert response.character_name == "TestHero"
        assert response.level == 1
        assert "успішно створений" in response.message

        # Перевіряємо що персонаж збережений в БД
        saved = repo.get_by_telegram_user_id(12345)
        assert saved is not None
        assert saved.name == "TestHero"

    def test_create_character_duplicate_user(self, db_session):
        """Тест створення дубліката персонажа"""
        # Arrange
        repo = PostgresCharacterRepository(db_session)
        use_case = CreateCharacterUseCase(repo)

        # Створюємо першого персонажа
        request1 = CreateCharacterRequest(
            telegram_user_id=23456,
            character_name="FirstHero"
        )
        use_case.execute(request1)
        db_session.commit()

        # Act & Assert - спроба створити другого
        request2 = CreateCharacterRequest(
            telegram_user_id=23456,
            character_name="SecondHero"
        )

        with pytest.raises(ValueError, match="вже існує"):
            use_case.execute(request2)

    def test_create_character_name_too_short(self, db_session):
        """Тест з занадто коротким іменем"""
        repo = PostgresCharacterRepository(db_session)
        use_case = CreateCharacterUseCase(repo)

        request = CreateCharacterRequest(
            telegram_user_id=34567,
            character_name="Ab"  # Лише 2 символи
        )

        with pytest.raises(ValueError, match="не менше 3 символів"):
            use_case.execute(request)

    def test_create_character_name_too_long(self, db_session):
        """Тест з занадто довгим іменем"""
        repo = PostgresCharacterRepository(db_session)
        use_case = CreateCharacterUseCase(repo)

        request = CreateCharacterRequest(
            telegram_user_id=45678,
            character_name="A" * 21  # 21 символ
        )

        with pytest.raises(ValueError, match="не більше 20 символів"):
            use_case.execute(request)
