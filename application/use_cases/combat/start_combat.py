"""
Use Case для початку бою.
"""
from dataclasses import dataclass
import random
from typing import Optional

from domain.repositories.character_repository import ICharacterRepository
from domain.repositories.enemy_repository import IEnemyRepository
from domain.repositories.location_repository import ILocationRepository  # Додано
from domain.services.stats_calculator import StatsCalculator

@dataclass
class StartCombatRequest:
    character_id: str
    enemy_id: Optional[str] = None

@dataclass
class StartCombatResponse:
    enemy_name: str
    enemy_health: int
    message: str

class StartCombatUseCase:
    def __init__(
        self,
        character_repo: ICharacterRepository,
        enemy_repo: IEnemyRepository,
        stats_calculator: StatsCalculator,
        location_repo: ILocationRepository  # Додано
    ):
        self.character_repo = character_repo
        self.enemy_repo = enemy_repo
        self.stats_calculator = stats_calculator
        self.location_repo = location_repo  # Додано

    def execute(self, request: StartCombatRequest) -> StartCombatResponse:
        character = self.character_repo.get(request.character_id)
        if not character:
            raise ValueError("Персонаж не знайдений")

        if character.combat_state:
            raise ValueError("Персонаж вже в бою")

        location = self.location_repo.get(character.location_id)
        if not location:
            raise ValueError("Локація персонажа не знайдена.")

        # --- Вибір ворога ---
        enemy_id = None
        if request.enemy_id:
            enemy_id = request.enemy_id
        elif location.enemy_pool:
            enemy_id = random.choice(location.enemy_pool)
        
        if not enemy_id:
            raise ValueError("В цій локації немає ворогів для бою.")

        enemy = self.enemy_repo.get_by_id(enemy_id)
        if not enemy:
            raise ValueError(f"Ворог з ID '{enemy_id}' не знайдений.")

        # --- Розрахунок характеристик ворога ---
        enemy_stats = self.stats_calculator.calculate_enemy_stats(enemy, character.level)

        # --- Оновлення стану персонажа ---
        character.combat_state = {
            "enemy_id": enemy_id,
            "enemy_level": enemy.level,
            "enemy_current_health": enemy_stats.max_health,
            "enemy_max_health": enemy_stats.max_health,
            "turn": 0
        }
        self.character_repo.save(character)

        return StartCombatResponse(
            message=f"Бій почався з {enemy.name}!",
            enemy_name=enemy.name,
            enemy_health=enemy_stats.max_health
        )