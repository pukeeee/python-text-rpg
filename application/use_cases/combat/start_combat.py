"""
Use Case для початку бою.
"""
from dataclasses import dataclass
import random
from typing import Optional

from domain.repositories.character_repository import ICharacterRepository
from domain.repositories.enemy_repository import IEnemyRepository
from domain.services.stats_calculator import StatsCalculator

@dataclass
class StartCombatRequest:
    character_id: str
    enemy_id: Optional[str] = None # Може бути None для випадкового ворога

@dataclass
class StartCombatResponse:
    combat_id: str
    character_health: int
    enemy_name: str
    enemy_health: int
    message: str

class StartCombatUseCase:
    def __init__(
        self,
        character_repo: ICharacterRepository,
        enemy_repo: IEnemyRepository,
        stats_calculator: StatsCalculator
    ):
        self.character_repo = character_repo
        self.enemy_repo = enemy_repo
        self.stats_calculator = stats_calculator

    def execute(self, request: StartCombatRequest) -> StartCombatResponse:
        character = self.character_repo.get(request.character_id)
        if not character:
            raise ValueError("Персонаж не знайдений")

        if character.combat_state:
            raise ValueError("Персонаж вже в бою")

        if request.enemy_id:
            enemy = self.enemy_repo.get_by_id(request.enemy_id)
        else:
            # Вибираємо випадкового ворога з локації
            enemies_in_location = self.enemy_repo.get_by_location(character.location_id)
            if not enemies_in_location:
                raise ValueError("В цій локації немає ворогів")
            enemy = random.choice(enemies_in_location)
        
        if not enemy:
            raise ValueError("Ворог не знайдений")

        # Розраховуємо характеристики гравця
        player_stats = self.stats_calculator.calculate_total_stats(character)

        # Створюємо стан бою
        combat_id = f"combat_{character.id}_{enemy.id}"
        character.combat_state = {
            "combat_id": combat_id,
            "enemy_id": enemy.id,
            "enemy_current_health": enemy.stats.max_health,
            "turn": 0
        }

        self.character_repo.save(character)

        return StartCombatResponse(
            combat_id=combat_id,
            character_health=player_stats.health,
            enemy_name=enemy.name,
            enemy_health=enemy.stats.max_health,
            message=f"Бій почався з {enemy.name}!"
        )
