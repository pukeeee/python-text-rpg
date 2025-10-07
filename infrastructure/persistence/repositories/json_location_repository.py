"""
Реалізація репозиторію локацій, що працює з JSON файлами.
"""
import os
import json
from typing import Optional, List

from domain.entities.location import Location
from domain.repositories.location_repository import ILocationRepository

class JsonLocationRepository(ILocationRepository):
    """Репозиторій для завантаження даних про локації з JSON файлів."""

    def __init__(self, data_path: str):
        self._locations: dict[str, Location] = {}
        self._locations_by_type: dict[str, List[str]] = {}
        self.data_path = data_path
        self._load_locations()

    def _load_locations(self):
        """Завантажує всі локації з файлів у вказаній директорії."""
        # data_path вже має бути коректним шляхом до папки data
        locations_dir = os.path.join(self.data_path, 'locations')
        if not os.path.isdir(locations_dir):
            return

        for filename in os.listdir(locations_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(locations_dir, filename)
                # Пропускаємо порожні файли
                if os.path.getsize(file_path) == 0:
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        # Отримуємо кожну локацію з файлу
                        # В файлі може бути один або багато об'єктів локацій
                        if isinstance(data, dict):
                            for location_id, location_data in data.items():
                                # Додаємо ID до даних для створення об'єкта Location
                                location_data['id'] = location_id
                                location = Location(**location_data)
                                self._locations[location.id] = location
                                
                                # Додаємо локацію до групи за типом
                                if location.type not in self._locations_by_type:
                                    self._locations_by_type[location.type] = []
                                self._locations_by_type[location.type].append(location.id)
                    except json.JSONDecodeError:
                        # Якщо файл не вдалося розібрати як JSON, пропускаємо
                        continue

    def get(self, location_id: str) -> Optional[Location]:
        """Отримує локацію за її ID."""
        return self._locations.get(location_id)

    def get_all(self) -> List[Location]:
        """Повертає список всіх завантажених локацій."""
        return list(self._locations.values())

    def get_by_type(self, location_type: str) -> List[Location]:
        """Отримує список локацій за типом."""
        location_ids = self._locations_by_type.get(location_type, [])
        return [self._locations[loc_id] for loc_id in location_ids if loc_id in self._locations]

    def get_all_types(self) -> List[str]:
        """Повертає список усіх наявних типів локацій."""
        return list(self._locations_by_type.keys())