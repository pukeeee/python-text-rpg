"""
Цей модуль визначає сутність Ворога (Enemy).
"""
from dataclasses import dataclass, field
from typing import Dict, Any

from domain.value_objects.enemy_stats import EnemyStats

@dataclass
class Enemy:
    """
    Сутність, що представляє ворога у грі.
    Має базові незмінні характеристики (stats) та динамічний стан (current_health).
    """
    id: str
    name: str
    level: int
    stats: EnemyStats
    experience_reward: int
    loot_table: Dict[str, Any]
    description: str
    current_health: int = field(init=False)

    def __post_init__(self):
        """Встановлює поточне здоров'я рівним максимальному після створення об'єкта."""
        self.current_health = self.stats.max_health

    def is_alive(self) -> bool:
        """Перевіряє, чи живий ворог."""
        return self.current_health > 0

    def take_damage(self, amount: int):
        """Накладає шкоду на ворога, зменшуючи поточне здоров'я."""
        if amount < 0:
            return
        self.current_health = max(0, self.current_health - amount)
