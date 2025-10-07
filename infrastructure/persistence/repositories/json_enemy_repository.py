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

class JsonEnemyRepository(IEnemyRepository):
    """
    Репозиторій, що завантажує дані про ворогів з JSON-файлів.
    """
    def __init__(self, data_path: str):
        self.data_path = data_path
        self._enemy_paths = self._find_all_enemy_files()

    def _find_all_enemy_files(self) -> Dict[str, str]:
        """Створює мапу ID ворога -> шлях до файлу."""
        enemy_paths = {}
        enemies_dir = os.path.join(self.data_path, 'enemies')
        if not os.path.isdir(enemies_dir):
            return {}
            
        for filename in os.listdir(enemies_dir):
            if filename.endswith('.json'):
                enemy_id = os.path.splitext(filename)[0]
                enemy_paths[enemy_id] = os.path.join(enemies_dir, filename)
        return enemy_paths

    @lru_cache(maxsize=32)
    def _get_by_id_cached(self, enemy_id: str) -> Optional[Enemy]:
        """Завантажує ворога за ID. Результат кешується."""
        file_path = self._enemy_paths.get(enemy_id)
        if not file_path or not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            stats_data = data.pop('stats', {})
            # Перейменовуємо 'health' в 'max_health' для сумісності з VO
            if 'health' in stats_data:
                stats_data['max_health'] = stats_data.pop('health')
            
            stats = EnemyStats(**stats_data)
            return Enemy(stats=stats, **data)

    def get_by_id(self, enemy_id: str) -> Optional[Enemy]:
        """Публічний метод, що викликає кешовану реалізацію."""
        return self._get_by_id_cached(enemy_id)

    def get_by_location(self, location_id: str) -> List[Enemy]:
        """
        Для MVP, повертаємо всіх ворогів. В майбутньому тут буде логіка
        фільтрації ворогів за локацією.
        """
        all_enemy_ids = list(self._enemy_paths.keys())
        return [enemy for enemy_id in all_enemy_ids if (enemy := self.get_by_id(enemy_id)) is not None]
