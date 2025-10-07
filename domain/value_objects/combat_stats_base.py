"""
Визначає базовий клас для всіх об'єктів, що містять бойові характеристики.
"""

class CombatStatsBase:
    """
    Базовий клас для об'єктів, що містять бойові характеристики.
    Визначає спільний інтерфейс для доступу до атрибутів, необхідних для бою.
    """
    accuracy: int
    evasion: int
    armor: int
    critical_chance: float
    critical_multiplier: float
    damage_min: int
    damage_max: int
    attack_speed: float
