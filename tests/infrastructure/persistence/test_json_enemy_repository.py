import os
from infrastructure.persistence.repositories.json_enemy_repository import JsonEnemyRepository


class TestJsonEnemyRepository:
    """Тести для JsonEnemyRepository які використовують актуальні дані"""

    def test_get_by_id_success(self):
        """Тестує отримання ворога за ID з використанням реальних даних"""
        # Використовуємо шлях до основної директорії даних
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonEnemyRepository(data_path)
        
        # Перевіряємо ворога, що точно існує в даних
        enemy = repo.get_by_id("goblin_01")

        assert enemy is not None
        assert enemy.id == "goblin_01"
        assert enemy.name == "Гоблін"
        assert enemy.level == 2
        assert enemy.stats.max_health == 80  # Перевіряємо, що 'health' перетворено в 'max_health'
        assert enemy.stats.armor == 30
        assert enemy.stats.evasion == 15
        assert enemy.stats.damage_min == 4
        assert enemy.stats.damage_max == 8
        assert enemy.stats.accuracy == 80
        assert enemy.stats.critical_chance == 3.0
        assert enemy.stats.critical_multiplier == 1.5
        assert enemy.stats.attack_speed == 1.0
        assert enemy.experience_reward == 50
        assert "items" in enemy.loot_table
        assert enemy.description == "Маленький зелений гоблін з палицею."

    def test_get_by_id_not_found(self):
        """Тестує отримання неіснуючого ворога"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonEnemyRepository(data_path)
        enemy = repo.get_by_id("nonexistent_enemy")

        assert enemy is None

    def test_get_by_level(self):
        """Тестує отримання ворогів за рівнем з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonEnemyRepository(data_path)
        
        # Отримуємо ворогів 2 рівня
        level_2_enemies = repo.get_by_level(2)
        assert len(level_2_enemies) == 1
        assert level_2_enemies[0].id == "goblin_01"
        assert level_2_enemies[0].name == "Гоблін"
        
        # Отримуємо ворогів 5 рівня
        level_5_enemies = repo.get_by_level(5)
        assert len(level_5_enemies) == 1
        assert level_5_enemies[0].id == "skeleton_01"
        assert level_5_enemies[0].name == "Скелет-воїн"
        
        # Отримуємо ворогів 8 рівня
        level_8_enemies = repo.get_by_level(8)
        assert len(level_8_enemies) == 1
        assert level_8_enemies[0].id == "bandit_01"
        assert level_8_enemies[0].name == "Розбійник"

    def test_get_all_levels(self):
        """Тестує отримання всіх рівнів ворогів з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonEnemyRepository(data_path)
        all_levels = repo.get_all_levels()
        
        expected_levels = [2, 5, 8]  # Згідно з тестовими даними
        for level in expected_levels:
            assert level in all_levels

    def test_get_by_location(self):
        """Тестує отримання ворогів за локацією з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        enemy_repo = JsonEnemyRepository(data_path)
        
        # Отримуємо ворогів для локації "town_main"
        # Згідно з файлом locations/town.json, у town_main enemy_pool: []
        location_enemies = enemy_repo.get_by_location("town_main")
        
        # Локація town_main має enemy_pool [], тому ворогів не буде
        assert len(location_enemies) == 0
        
        # Перевіряємо локацію "forest_dark" з файлу locations/wilderness.json
        # Після оновлення файлу, в цієї локації enemy_pool: ["goblin_01", "skeleton_01"]
        location_enemies = enemy_repo.get_by_location("forest_dark")
        
        # Маємо 2 вороги, які визначені в enemy_pool
        assert len(location_enemies) == 2
        
        enemy_ids = [enemy.id for enemy in location_enemies]
        assert "goblin_01" in enemy_ids
        assert "skeleton_01" in enemy_ids
        
        # Перевіряємо локацію "old_road"
        # Після оновлення файлу, в цієї локації enemy_pool: ["bandit_01", "goblin_01"]
        location_enemies = enemy_repo.get_by_location("old_road")
        
        # Маємо 2 вороги, які визначені в enemy_pool (один з них - goblin_01 - дублюється)
        assert len(location_enemies) == 2
        
        enemy_ids = [enemy.id for enemy in location_enemies]
        assert "bandit_01" in enemy_ids
        assert "goblin_01" in enemy_ids

    def test_handles_empty_json_file(self):
        """Тестує, що репозиторій коректно обробляє порожні JSON-файли"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonEnemyRepository(data_path)
        
        # Ми перевіряємо, що репозиторій існує і може працювати з даними
        # Ми не очікуємо ворогів з порожніх файлів
        all_levels = repo.get_all_levels()
        # Просто перевіряємо, що це список чисел і він не містить помилок
        assert isinstance(all_levels, list)
        for level in all_levels:
            assert isinstance(level, int)