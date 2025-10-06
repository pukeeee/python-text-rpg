"""
Цей модуль визначає абстрактні інтерфейси репозиторіїв.

Інтерфейс репозиторію - це "контракт" у доменному шарі, який описує, які методи
для роботи з даними має надавати шар інфраструктури. Це дозволяє домену
не залежати від конкретної реалізації бази даних.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from domain.entities.character import Character

class ICharacterRepository(ABC):
    """
    Інтерфейс для репозиторію персонажів, що визначає контракт
    для збереження, завантаження та управління даними персонажів.
    """

    @abstractmethod
    def save(self, character: Character) -> None:
        """
        Зберігає або оновлює дані персонажа.

        :param character: Об'єкт персонажа для збереження.
        """
        pass

    @abstractmethod
    def get(self, character_id: str) -> Optional[Character]:
        """
        Знаходить персонажа за його унікальним ідентифікатором.

        :param character_id: ID персонажа.
        :return: Об'єкт персонажа або None, якщо не знайдено.
        """
        pass

    @abstractmethod
    def get_by_telegram_user_id(self, telegram_user_id: int) -> Optional[Character]:
        """
        Знаходить персонажа за його ідентифікатором користувача Telegram.

        :param telegram_user_id: ID користувача в Telegram.
        :return: Об'єкт персонажа або None, якщо не знайдено.
        """
        pass

    @abstractmethod
    def delete(self, character_id: str) -> None:
        """
        Видаляє персонажа за його ідентифікатором.

        :param character_id: ID персонажа для видалення.
        """
        pass

    @abstractmethod
    def save_stats_cache(self, character_id: str, stats: Dict[str, Any], equipment_items: List[str]) -> None:
        """
        Зберігає кешовані характеристики персонажа.

        Примітка: для максимальної типізації `stats` може бути не словником,
        а окремим DTO (Data Transfer Object), наприклад, `CalculatedStatsDTO`.

        :param character_id: ID персонажа.
        :param stats: Словник з розрахованими характеристиками.
        :param equipment_items: Список ID предметів екіпіровки для розрахунку хешу.
        """
        pass

    @abstractmethod
    def get_stats_cache(self, character_id: str, equipment_items: List[str]) -> Optional[Dict[str, Any]]:
        """
        Отримує кешовані характеристики, якщо вони актуальні.

        Примітка: для максимальної типізації повернений тип може бути не словником,
        а окремим DTO (Data Transfer Object), наприклад, `CalculatedStatsDTO`.

        :param character_id: ID персонажа.
        :param equipment_items: Список ID предметів для перевірки актуальності кешу.
        :return: Словник з характеристиками або None, якщо кеш неактуальний.
        """
        pass