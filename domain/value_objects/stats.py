"""
Цей модуль визначає Об'єкти-значення (Value Objects), пов'язані зі світом гри.

Об'єкти-значення - це незмінні об'єкти, які визначаються своїми атрибутами.
Два об'єкти-значення з однаковими атрибутами вважаються однаковими.
"""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class BaseStats:
    """
    Об'єкт-значення, що представляє базові (незмінні) характеристики персонажа.
    Використання `frozen=True` гарантує, що екземпляр цього класу не можна буде змінити
    після створення, що є ключовою властивістю об'єктів-значень.
    """
    strength: int
    dexterity: int
    intelligence: int
    base_health: int
    base_mana: int

    def with_level_up(self) -> 'BaseStats':
        """Создать новый объект с увеличенными характеристиками"""
        return replace(
            self,
            strength=self.strength + 2,
            dexterity=self.dexterity + 2,
            intelligence=self.intelligence + 2,
            base_health=self.base_health + 10,
            base_mana=self.base_mana + 5
        )


# domain/value_objects/stats.py - ДОПОЛНИТЬ:

@dataclass(frozen=True)
class Stats:
    """Полный набор характеристик персонажа (рассчитанных)"""
    # Базовые
    strength: int
    dexterity: int
    intelligence: int

    # Здоровье и мана
    health: int
    max_health: int
    mana: int
    max_mana: int

    # Защита
    armor: int
    evasion: int
    energy_shield: int

    # Атака
    damage_min: int
    damage_max: int
    accuracy: int
    critical_chance: float
    critical_multiplier: float
    attack_speed: float
