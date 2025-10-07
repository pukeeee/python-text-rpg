"""
Реалізація репозиторію для завантаження предметів з JSON-файлів.
"""
import json
import os
from typing import Optional, List, Dict, Literal
from functools import lru_cache

from domain.entities.item import Item
from domain.repositories.item_repository import IItemRepository

ItemType = Literal["weapon", "armor", "helmet", "consumable", "amulet", "boots", "chest", "gloves", "ring"]

class JsonItemRepository(IItemRepository):
    """
    Репозиторій, що завантажує дані про предмети з JSON-файлів.
    Використовує кешування для уникнення повторного читання файлів.
    """
    def __init__(self, data_path: str):
        self.data_path = data_path
        self._item_paths = self._find_all_item_files()
        self._items_by_type = self._organize_items_by_type()

    def _find_all_item_files(self) -> Dict[str, str]:
        """Знаходить всі JSON-файли предметів і створює мапу ID предметів -> шлях."""
        item_paths = {}
        items_dir = os.path.join(self.data_path, 'items')
        if not os.path.isdir(items_dir):
            return {}
            
        for root, _, files in os.walk(items_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    # Пропускаємо порожні файли
                    if os.path.getsize(file_path) == 0:
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Для кожного предмета в файлі додаємо відображення ID -> файл
                            for item_id in data.keys():
                                item_paths[item_id] = file_path
                    except json.JSONDecodeError:
                        # Якщо файл не вдалося розібрати як JSON, пропускаємо
                        continue
        return item_paths

    def _organize_items_by_type(self) -> Dict[str, List[str]]:
        """Організовує ID предметів за їх типом."""
        items_by_type = {}
        
        for item_id, file_path in self._item_paths.items():
            # Отримуємо тип предмета з файлу
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Отримуємо конкретний предмет за ID із загального файлу
                    item_data = data.get(item_id)
                    if item_data:
                        item_type = item_data.get('type', 'unknown')
                        
                        if item_type not in items_by_type:
                            items_by_type[item_type] = []
                        items_by_type[item_type].append(item_id)
            except json.JSONDecodeError:
                # Якщо файл не вдалося розібрати як JSON, додаємо як 'unknown'
                item_type = 'unknown'
                
                if item_type not in items_by_type:
                    items_by_type[item_type] = []
                items_by_type[item_type].append(item_id)
                
        return items_by_type

    def _get_item_from_file(self, item_id: str) -> Optional[Item]:
        """Завантажує предмет з файлу за ID без використання кешу."""
        file_path = self._item_paths.get(item_id)
        if not file_path or not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Отримуємо конкретний предмет за ID з файлу
            item_data = data.get(item_id)
            if item_data:
                # Якщо поле id відсутнє в даних, додаємо його
                if 'id' not in item_data:
                    item_data['id'] = item_id
                return Item(**item_data)
            else:
                return None

    @lru_cache(maxsize=128)
    def _get_by_id_cached(self, item_id: str) -> Optional[Item]:
        """Завантажує предмет за ID. Результат кешується."""
        file_path = self._item_paths.get(item_id)
        if not file_path or not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Отримуємо конкретний предмет за ID з файлу
            item_data = data.get(item_id)
            if item_data:
                # Якщо поле id відсутнє в даних, додаємо його
                if 'id' not in item_data:
                    item_data['id'] = item_id
                
                # Окремо обробляємо поле effects, якщо воно є
                effects = item_data.pop('effects', None)
                
                # Створюємо предмет
                item = Item(**item_data)
                
                # Якщо є effects, встановлюємо їх окремо
                if effects is not None:
                    # Для цього нам потрібно оновити створення об'єкта
                    # Потрібно створити об'єкт з усіма атрибутами, включаючи effects
                    updated_item_data = item_data.copy()
                    updated_item_data['effects'] = effects
                    return Item(**updated_item_data)
                
                return item
            else:
                return None

    def get_by_id(self, item_id: str) -> Optional[Item]:
        """Публічний метод, що викликає кешовану реалізацію."""
        return self._get_by_id_cached(item_id)

    def get_many_by_ids(self, item_ids: List[str]) -> List[Item]:
        """Завантажує декілька предметів за списком ID."""
        result = []
        for item_id in item_ids:
            item = self.get_by_id(item_id)
            if item:
                result.append(item)
        return result

    def get_by_type(self, item_type: ItemType) -> List[Item]:
        """Отримує список предметів за типом."""
        item_ids = self._items_by_type.get(item_type, [])
        return [item for item_id in item_ids if (item := self.get_by_id(item_id)) is not None]
        
    def get_all_types(self) -> List[str]:
        """Повертає список усіх наявних типів предметів."""
        return list(self._items_by_type.keys())
