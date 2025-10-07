"""
Цей модуль визначає інтерфейс для репозиторію локацій.
"""
from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.location import Location

class ILocationRepository(ABC):
    """Абстрактний базовий клас для репозиторію локацій."""

    @abstractmethod
    def get(self, location_id: str) -> Optional[Location]:
        """Отримує локацію за її ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Location]:
        """Отримує всі локації."""
        pass