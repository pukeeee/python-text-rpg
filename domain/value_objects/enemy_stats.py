"""
Визначає Value Object для характеристик ворога.
"""
from dataclasses import dataclass

from .combat_stats_base import CombatStatsBase

@dataclass(frozen=True)
class EnemyStats(CombatStatsBase):
    """Незмінний об'єкт, що містить базові бойові характеристики ворога."""
    max_health: int
    armor: int
    evasion: int
    damage_min: int
    damage_max: int
    accuracy: int
    critical_chance: float
    critical_multiplier: float
    attack_speed: float
