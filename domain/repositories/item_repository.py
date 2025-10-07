"""
Інтерфейс для репозиторію предметів.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.item import Item

class IItemRepository(ABC):
    """
    Абстрактний репозиторій для доступу до даних про предмети.
    """

    @abstractmethod
    def get_by_id(self, item_id: str) -> Optional[Item]:
        """Знаходить предмет за його ID."""
        pass

    @abstractmethod
    def get_many_by_ids(self, item_ids: List[str]) -> List[Item]:
        """Знаходить декілька предметів за їх ID."""
        pass
