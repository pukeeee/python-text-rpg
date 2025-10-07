"""
Реалізація репозиторію для завантаження предметів з JSON-файлів.
"""
import json
import os
from typing import Optional, List, Dict
from functools import lru_cache

from domain.entities.item import Item
from domain.repositories.item_repository import IItemRepository

class JsonItemRepository(IItemRepository):
    """
    Репозиторій, що завантажує дані про предмети з JSON-файлів.
    Використовує кешування для уникнення повторного читання файлів.
    """
    def __init__(self, data_path: str):
        self.data_path = data_path
        self._item_paths = self._find_all_item_files()

    def _find_all_item_files(self) -> Dict[str, str]:
        """Знаходить всі JSON-файли предметів і створює мапу ID -> шлях."""
        item_paths = {}
        for root, _, files in os.walk(self.data_path):
            for file in files:
                if file.endswith('.json'):
                    item_id = os.path.splitext(file)[0]
                    item_paths[item_id] = os.path.join(root, file)
        return item_paths

    @lru_cache(maxsize=128)
    def _get_by_id_cached(self, item_id: str) -> Optional[Item]:
        """Завантажує предмет за ID. Результат кешується."""
        file_path = self._item_paths.get(item_id)
        if not file_path or not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Item(**data)

    def get_by_id(self, item_id: str) -> Optional[Item]:
        """Публічний метод, що викликає кешовану реалізацію."""
        return self._get_by_id_cached(item_id)

    def get_many_by_ids(self, item_ids: List[str]) -> List[Item]:
        """Завантажує декілька предметів за списком ID."""
        return [item for item_id in item_ids if (item := self.get_by_id(item_id)) is not None]
