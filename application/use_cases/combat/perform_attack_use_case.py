"""
Use Case для виконання атаки в бою.
"""
from dataclasses import dataclass, field
from typing import List, Optional

from domain.repositories.character_repository import ICharacterRepository
from domain.repositories.enemy_repository import IEnemyRepository
from domain.services.stats_calculator import StatsCalculator
from domain.services.combat_calculator import CombatCalculator
from domain.services.loot_generator import LootGenerator

@dataclass
class AttackResultDTO:
    attacker: str
    defender: str
    is_hit: bool
    is_critical: bool
    damage: int
    defender_health_remaining: int

@dataclass
class CombatRewardsDTO:
    experience_gained: int
    gold_gained: int
    items_gained: List[str]
    level_up: bool = False

@dataclass
class PerformAttackRequest:
    character_id: str
    number_of_attacks: int = 1

@dataclass
class PerformAttackResponse:
    combat_ended: bool
    victor: Optional[str]
    player_attacks: List[AttackResultDTO] = field(default_factory=list)
    enemy_attacks: List[AttackResultDTO] = field(default_factory=list)
    rewards: Optional[CombatRewardsDTO] = None
    message: str = ""

class PerformAttackUseCase:
    def __init__(
        self,
        character_repo: ICharacterRepository,
        enemy_repo: IEnemyRepository,
        stats_calculator: StatsCalculator,
        combat_calculator: CombatCalculator,
        loot_generator: LootGenerator
    ):
        self.character_repo = character_repo
        self.enemy_repo = enemy_repo
        self.stats_calculator = stats_calculator
        self.combat_calculator = combat_calculator
        self.loot_generator = loot_generator

    def execute(self, request: PerformAttackRequest) -> PerformAttackResponse:
        character = self.character_repo.get(request.character_id)
        if not character or not character.combat_state:
            raise ValueError("Персонаж не в бою")

        enemy = self.enemy_repo.get_by_id(character.combat_state['enemy_id'])
        if not enemy:
            raise ValueError("Ворог в бою не знайдений")
        
        enemy.current_health = character.combat_state['enemy_current_health']

        player_stats = self.stats_calculator.calculate_total_stats(character)
        enemy_stats = enemy.stats

        player_attack_results = []
        enemy_attack_results = []

        # Атаки гравця
        for _ in range(request.number_of_attacks):
            if not enemy.is_alive(): break
            is_hit, is_crit, damage = self.combat_calculator.perform_single_attack(player_stats, enemy_stats)
            if is_hit:
                enemy.take_damage(damage)
            player_attack_results.append(AttackResultDTO("player", "enemy", is_hit, is_crit, damage, enemy.current_health))

        # Перевірка на перемогу гравця
        if not enemy.is_alive():
            rewards_data = self.loot_generator.generate_loot(enemy.loot_table)
            leveled_up = character.gain_experience(enemy.experience_reward)
            for item_id in rewards_data['items']:
                character.add_item(item_id)
            
            rewards = CombatRewardsDTO(
                experience_gained=enemy.experience_reward,
                gold_gained=rewards_data['gold'],
                items_gained=rewards_data['items'],
                level_up=leveled_up
            )
            character.combat_state = None
            self.character_repo.save(character)
            return PerformAttackResponse(True, "player", player_attack_results, [], rewards, "Перемога!")

        # Атаки ворога
        for _ in range(request.number_of_attacks):
            if not character.is_alive(): break
            is_hit, is_crit, damage = self.combat_calculator.perform_single_attack(enemy_stats, player_stats)
            if is_hit:
                character.take_damage(damage)
            enemy_attack_results.append(AttackResultDTO("enemy", "player", is_hit, is_crit, damage, character.current_health))

        # Перевірка на поразку гравця
        if not character.is_alive():
            character.combat_state = None
            self.character_repo.save(character)
            return PerformAttackResponse(True, "enemy", player_attack_results, enemy_attack_results, None, "Поразка...")

        # Оновлення стану бою
        character.combat_state['enemy_current_health'] = enemy.current_health
        character.combat_state['turn'] += 1
        self.character_repo.save(character)

        return PerformAttackResponse(False, None, player_attack_results, enemy_attack_results, None, "Бій триває...")