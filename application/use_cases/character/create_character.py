from domain.entities.character import Character
from domain.value_objects.stats import BaseStats
from domain.repositories.character_repository import ICharacterRepository
from application.dto.character_dto import CreateCharacterRequest, CreateCharacterResponse

class CreateCharacterUseCase:
    """Use Case для створення нового персонажа"""

    def __init__(self, character_repository: ICharacterRepository):
        self.character_repository = character_repository

    def execute(self, request: CreateCharacterRequest) -> CreateCharacterResponse:
        """
        Створює нового персонажа з базовими характеристиками

        Raises:
            ValueError: Якщо персонаж з таким telegram_user_id вже існує
        """
        # Перевіряємо чи не існує вже персонаж для цього користувача
        existing = self.character_repository.get_by_telegram_user_id(request.telegram_user_id)
        if existing:
            raise ValueError(f"Персонаж для користувача {request.telegram_user_id} вже існує")

        # Валідація імені
        if len(request.character_name) < 3:
            raise ValueError("Ім'я персонажа має бути не менше 3 символів")
        if len(request.character_name) > 20:
            raise ValueError("Ім'я персонажа має бути не більше 20 символів")

        # Створюємо персонажа з базовими характеристиками
        base_stats = BaseStats(
            strength=10,
            dexterity=10,
            intelligence=10,
            base_health=100,
            base_mana=50
        )

        character = Character(
            telegram_user_id=request.telegram_user_id,
            name=request.character_name,
            base_stats=base_stats
        )

        # Зберігаємо в репозиторій
        self.character_repository.save(character)

        return CreateCharacterResponse(
            character_id=character.id,
            character_name=character.name,
            level=character.level,
            message=f"Персонаж {character.name} успішно створений!"
        )
