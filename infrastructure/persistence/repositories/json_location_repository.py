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
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    location = Location(**data)
                    self._locations[location.id] = location

    def get(self, location_id: str) -> Optional[Location]:
        """Отримує локацію за її ID."""
        return self._locations.get(location_id)

    def get_all(self) -> List[Location]:
        """Повертає список всіх завантажених локацій."""
        return list(self._locations.values())