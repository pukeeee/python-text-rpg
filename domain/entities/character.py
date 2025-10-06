"""
Цей модуль визначає ключові бізнес-сутності (Entities) домену.

Сутність - це об'єкт з унікальним ID, що має тривалий життєвий цикл і містить
ключову бізнес-логіку, пов'язану з собою.
"""
from typing import List, Dict, Optional
from domain.value_objects import BaseStats
import uuid

class Character:
    """
    Головна сутність гри, що представляє персонажа. Інкапсулює в собі стан
    та поведінку персонажа.

    Це "багата" доменна модель: вона містить не лише дані, а й методи,
    що реалізують бізнес-логіку (напр., отримання шкоди).
    """
    def __init__(
        self,
        telegram_user_id: int, # ID користувача в Telegram, для зв'язку.
        name: str, # Ім'я персонажа.
        base_stats: BaseStats, # Базові, незмінні характеристики.
        level: int = 1,
        experience: int = 0,
        current_health: Optional[int] = None, # Поточне здоров'я.
        current_mana: Optional[int] = None, # Поточна мана.
        equipped_items: Optional[Dict[str, Optional[str]]] = None, # Словник з ID екіпірованих предметів.
        inventory: Optional[List[str]] = None, # Список ID предметів в інвентарі.
        location_id: str = 'town_main', # Поточна локація персонажа.
        combat_state: Optional[dict] = None, # Стан бою, якщо персонаж у бою.
        id: Optional[str] = None # Унікальний ID персонажа.
    ):
        # --- Ініціалізація атрибутів ---
        self.id = id or str(uuid.uuid4())
        self.telegram_user_id = telegram_user_id
        self.name = name
        self.level = level
        self.experience = experience
        self.base_stats = base_stats

        # Якщо поточне здоров'я/мана не передані, вони дорівнюють базовим.
        # Це зручно при створенні нового персонажа.
        self.current_health = current_health if current_health is not None else base_stats.base_health
        self.current_mana = current_mana if current_mana is not None else base_stats.base_mana

        self.equipped_items = equipped_items or {}
        self.inventory = inventory or []
        self.location_id = location_id
        self.combat_state = combat_state

    # --- Бізнес-логіка, інкапсульована в сутності ---

    def is_alive(self) -> bool:
        """Перевіряє, чи живий персонаж."""
        return self.current_health > 0

    def take_damage(self, amount: int) -> None:
        """
        Накладає шкоду на персонажа.
        Запобігає падінню здоров'я нижче нуля.
        """
        if amount < 0:
            return # Не можна нанести негативну шкоду.

        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0

    # --- Представлення об'єкта ---

    def __repr__(self) -> str:
        """Повертає рядкове представлення об'єкта для дебагу."""
        return f"<Character {self.name} (Lvl: {self.level})>"