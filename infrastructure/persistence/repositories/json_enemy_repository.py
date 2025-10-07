"""
Реалізація репозиторію для завантаження ворогів з JSON-файлів.
"""
import json
import os
from typing import Optional, List, Dict
from functools import lru_cache

from domain.entities.enemy import Enemy
from domain.repositories.enemy_repository import IEnemyRepository
from domain.value_objects.enemy_stats import EnemyStats
from .json_location_repository import JsonLocationRepository

class JsonEnemyRepository(IEnemyRepository):
    """
    Репозиторій, що завантажує дані про ворогів з JSON-файлів.
    """
    def __init__(self, data_path: str):
        self.data_path = data_path
        self._enemy_paths = self._find_all_enemy_files()
        self._enemies_by_level = self._organize_enemies_by_level()

    def _find_all_enemy_files(self) -> Dict[str, str]:
        """Створює мапу ID ворога -> шлях до файлу."""
        enemy_paths = {}
        enemies_dir = os.path.join(self.data_path, 'enemies')
        if not os.path.isdir(enemies_dir):
            return {}
            
        for root, _, files in os.walk(enemies_dir):
            for filename in files:
                if filename.endswith('.json'):
                    file_path = os.path.join(root, filename)
                    # Пропускаємо порожні файли
                    if os.path.getsize(file_path) == 0:
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Для кожного ворога в файлі додаємо відображення ID -> файл
                            for enemy_id in data.keys():
                                enemy_paths[enemy_id] = file_path
                    except json.JSONDecodeError:
                        # Якщо файл не вдалося розібрати як JSON, пропускаємо
                        continue
        return enemy_paths

    def _organize_enemies_by_level(self) -> Dict[int, List[str]]:
        """Організовує ID ворогів за їх рівнем."""
        enemies_by_level = {}
        
        for enemy_id in self._enemy_paths.keys():
            # Завантажуємо ворога тимчасово, щоб визначити його рівень
            enemy = self._get_enemy_from_file(enemy_id)
            if enemy:
                level = enemy.level
                if level not in enemies_by_level:
                    enemies_by_level[level] = []
                enemies_by_level[level].append(enemy_id)
                
        return enemies_by_level

    def _get_enemy_from_file(self, enemy_id: str) -> Optional[Enemy]:
        """Завантажує ворога з файлу за ID без використання кешу."""
        file_path = self._enemy_paths.get(enemy_id)
        if not file_path or not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Отримуємо конкретного ворога за ID з файлу
            enemy_data = data.get(enemy_id)
            if enemy_data:
                stats_data = enemy_data.pop('stats', {})
                # Перейменовуємо 'health' в 'max_health' для сумісності з VO
                if 'health' in stats_data:
                    stats_data['max_health'] = stats_data.pop('health')
                
                stats = EnemyStats(**stats_data)
                # Додаємо ID до даних
                if 'id' not in enemy_data:
                    enemy_data['id'] = enemy_id
                return Enemy(stats=stats, **enemy_data)
            else:
                return None

    @lru_cache(maxsize=32)
    def _get_by_id_cached(self, enemy_id: str) -> Optional[Enemy]:
        """Завантажує ворога за ID. Результат кешується."""
        file_path = self._enemy_paths.get(enemy_id)
        if not file_path or not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Отримуємо конкретного ворога за ID з файлу
            enemy_data = data.get(enemy_id)
            if enemy_data:
                stats_data = enemy_data.pop('stats', {})
                # Перейменовуємо 'health' в 'max_health' для сумісності з VO
                if 'health' in stats_data:
                    stats_data['max_health'] = stats_data.pop('health')
                
                stats = EnemyStats(**stats_data)
                # Додаємо ID до даних
                if 'id' not in enemy_data:
                    enemy_data['id'] = enemy_id
                return Enemy(stats=stats, **enemy_data)
            else:
                return None

    def get_by_id(self, enemy_id: str) -> Optional[Enemy]:
        """Публічний метод, що викликає кешовану реалізацію."""
        return self._get_by_id_cached(enemy_id)

    def get_by_location(self, location_id: str) -> List[Enemy]:
        """
        Повертає список ворогів, доступних у певній локації.
        Використовує мапу ворогів з файлів локацій для визначення доступних ворогів.
        """
        # Створюємо новий репозиторій локацій для отримання інформації про локацію
        location_repo = JsonLocationRepository(self.data_path)
        location = location_repo.get(location_id)
        
        if not location:
            return []
        
        # Отримуємо список можливих ворогів з локації
        enemy_pool = location.enemy_pool
        if not enemy_pool:
            return []
        
        # Якщо в локації є конкретні ID ворогів
        specific_enemies = [enemy_id for enemy_id in enemy_pool if enemy_id in self._enemy_paths]
        enemies = []
        
        for enemy_id in specific_enemies:
            enemy = self.get_by_id(enemy_id)
            if enemy:
                enemies.append(enemy)
        
        return enemies

    def get_by_level(self, level: int) -> List[Enemy]:
        """Отримує список ворогів за рівнем."""
        enemy_ids = self._enemies_by_level.get(level, [])
        return [enemy for enemy_id in enemy_ids if (enemy := self.get_by_id(enemy_id)) is not None]

    def get_all_levels(self) -> List[int]:
        """Повертає список усіх наявних рівнів ворогів."""
        return sorted(list(self._enemies_by_level.keys()))
