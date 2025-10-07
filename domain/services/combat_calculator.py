"""
Сервіс для всіх розрахунків, пов'язаних з бойовою системою.
"""
import random
from typing import Tuple

from domain.value_objects.damage_range import DamageRange
from domain.value_objects.combat_stats_base import CombatStatsBase

class CombatCalculator:
    """Інкапсулює логіку розрахунку шкоди, шансів попадання, критів тощо."""

    MIN_HIT_CHANCE = 0.05
    MAX_HIT_CHANCE = 0.95
    MIN_DAMAGE = 1

    def calculate_hit_chance(
        self,
        attacker_accuracy: int,
        defender_evasion: int
    ) -> float:
        """
        Розрахунок шансу попадання.
        Формула: accuracy / (accuracy + evasion / 4)
        """
        if attacker_accuracy <= 0:
            return self.MIN_HIT_CHANCE

        raw_chance = attacker_accuracy / (attacker_accuracy + defender_evasion / 4)
        return max(self.MIN_HIT_CHANCE, min(self.MAX_HIT_CHANCE, raw_chance))

    def is_hit(self, attacker_accuracy: int, defender_evasion: int) -> bool:
        """Визначає, чи була атака успішною."""
        hit_chance = self.calculate_hit_chance(attacker_accuracy, defender_evasion)
        return random.random() < hit_chance

    def is_critical_hit(self, critical_chance: float) -> bool:
        """Визначає, чи був удар критичним."""
        return random.uniform(0, 100) < critical_chance

    def calculate_damage(
        self,
        damage_range: DamageRange,
        target_armor: int,
        is_critical: bool = False,
        critical_multiplier: float = 1.5
    ) -> int:
        """
        Розраховує фінальну шкоду з урахуванням всіх модифікаторів.
        """
        base_damage = random.randint(damage_range.min_damage, damage_range.max_damage)

        if is_critical:
            base_damage = int(base_damage * critical_multiplier)

        # Формула зменшення шкоди від броні (спрощена версія PoE)
        damage_multiplier = base_damage / (base_damage + target_armor)
        final_damage = base_damage * damage_multiplier

        return max(self.MIN_DAMAGE, int(final_damage))

    def perform_single_attack(
        self,
        attacker_stats: CombatStatsBase,
        defender_stats: CombatStatsBase
    ) -> Tuple[bool, bool, int]:
        """
        Симулює одну повну атаку та повертає результат.

        :return: Tuple (is_hit, is_critical, damage_dealt)
        """
        if not self.is_hit(attacker_stats.accuracy, defender_stats.evasion):
            return False, False, 0

        is_crit = self.is_critical_hit(attacker_stats.critical_chance)

        damage = self.calculate_damage(
            damage_range=DamageRange(attacker_stats.damage_min, attacker_stats.damage_max),
            target_armor=defender_stats.armor,
            is_critical=is_crit,
            critical_multiplier=attacker_stats.critical_multiplier
        )

        return True, is_crit, damage