from domain.repositories.character_repository import ICharacterRepository
from domain.services.stats_calculator import StatsCalculator
from application.dto.character_dto import (
    GetCharacterStatsRequest,
    GetCharacterStatsResponse,
    StatsDTO
)

class GetCharacterStatsUseCase:
    """Use Case для отримання характеристик персонажа"""

    def __init__(
        self,
        character_repository: ICharacterRepository,
        stats_calculator: StatsCalculator
    ):
        self.character_repository = character_repository
        self.stats_calculator = stats_calculator

    def execute(self, request: GetCharacterStatsRequest) -> GetCharacterStatsResponse:
        """
        Отримує та розраховує всі характеристики персонажа

        Raises:
            ValueError: Якщо персонаж не знайдений
        """
        # Отримуємо персонажа
        character = self.character_repository.get_by_telegram_user_id(request.telegram_user_id)
        if not character:
            raise ValueError(f"Персонаж для користувача {request.telegram_user_id} не знайдений")

        # Розраховуємо характеристики
        stats = self.stats_calculator.calculate_total_stats(character)

        # Розраховуємо досвід до наступного рівня
        exp_to_next = int(100 * (1.5 ** (character.level - 1)))

        # Перетворюємо в DTO
        stats_dto = StatsDTO(
            strength=stats.strength,
            dexterity=stats.dexterity,
            intelligence=stats.intelligence,
            health=stats.health,
            max_health=stats.max_health,
            mana=stats.mana,
            max_mana=stats.max_mana,
            armor=stats.armor,
            evasion=stats.evasion,
            energy_shield=stats.energy_shield,
            damage_min=stats.damage_min,
            damage_max=stats.damage_max,
            accuracy=stats.accuracy,
            critical_chance=stats.critical_chance,
            critical_multiplier=stats.critical_multiplier,
            attack_speed=stats.attack_speed
        )

        return GetCharacterStatsResponse(
            character_id=character.id,
            name=character.name,
            level=character.level,
            experience=character.experience,
            experience_to_next_level=exp_to_next,
            stats=stats_dto,
            location=character.location_id
        )
