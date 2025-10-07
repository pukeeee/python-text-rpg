"""
Інтерфейс для репозиторію ворогів.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.enemy import Enemy

class IEnemyRepository(ABC):
    """
    Абстрактний репозиторій для доступу до даних про ворогів.
    """

    @abstractmethod
    def get_by_id(self, enemy_id: str) -> Optional[Enemy]:
        """Знаходить ворога за його ID."""
        pass

    @abstractmethod
    def get_by_location(self, location_id: str) -> List[Enemy]:
        """Повертає список ворогів, доступних у певній локації."""
        pass
