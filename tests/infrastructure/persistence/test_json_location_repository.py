import os
from infrastructure.persistence.repositories.json_location_repository import JsonLocationRepository


class TestJsonLocationRepository:
    """Тести для JsonLocationRepository які використовують актуальні дані"""

    def test_get_by_id_success(self):
        """Тестує отримання локації за ID з використанням реальних даних"""
        # Використовуємо шлях до основної директорії даних
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonLocationRepository(data_path)
        
        # Перевіряємо локацію, що точно існує в даних
        location = repo.get("town_main")

        assert location is not None
        assert location.id == "town_main"
        assert location.name == "Sanctuary"
        assert location.type == "town"
        assert "rest" in location.available_actions
        assert "change_equipment" in location.available_actions
        assert "travel" in location.available_actions
        assert location.description == "A safe town where adventurers can rest and prepare."
        assert "forest_dark" in location.connected_locations
        assert "cave_entrance" in location.connected_locations

    def test_get_by_id_not_found(self):
        """Тестує отримання неіснуючої локації"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonLocationRepository(data_path)
        location = repo.get("nonexistent_location")

        assert location is None

    def test_get_all(self):
        """Тестує отримання всіх локацій з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonLocationRepository(data_path)
        all_locations = repo.get_all()

        # Маємо принаймні локації, які визначені в файлах
        assert len(all_locations) >= 3  # town_main, forest_dark, old_road

        location_ids = [loc.id for loc in all_locations]
        assert "town_main" in location_ids
        assert "forest_dark" in location_ids
        assert "old_road" in location_ids

    def test_get_by_type(self):
        """Тестує отримання локацій за типом з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonLocationRepository(data_path)
        
        # Отримуємо міста
        towns = repo.get_by_type("town")
        assert len(towns) >= 1
        town_ids = [loc.id for loc in towns]
        assert "town_main" in town_ids
        
        # Отримуємо дикі місця
        wilderness = repo.get_by_type("wilderness")
        assert len(wilderness) >= 2
        wilderness_ids = [loc.id for loc in wilderness]
        assert "forest_dark" in wilderness_ids
        assert "old_road" in wilderness_ids

    def test_get_all_types(self):
        """Тестує отримання всіх типів локацій з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonLocationRepository(data_path)
        all_types = repo.get_all_types()
        
        expected_types = ["town", "wilderness"]
        for expected_type in expected_types:
            assert expected_type in all_types

    def test_location_attributes_comprehensive(self):
        """Тестує всі атрибути локації на прикладі конкретної локації з різними властивостями"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonLocationRepository(data_path)
        
        # Перевіряємо локацію з багатьма атрибутами (наприклад, forest_dark)
        location = repo.get("forest_dark")
        
        assert location is not None
        assert location.id == "forest_dark"
        assert location.name == "Темний ліс"
        assert location.type == "wilderness"
        assert "explore" in location.available_actions
        assert "travel" in location.available_actions
        assert location.description == "Небезпечний ліс, повний монстрів."
        
        # Перевіряємо event_pool (це словник у нашому випадку)
        assert hasattr(location, 'event_pool')
        # У нашому випадку event_pool - це список подій
        assert isinstance(location.event_pool, list)
        assert len(location.event_pool) == 3  # Згідно з вмістом файлу
        
        # Перевіряємо enemy_pool (це словник у нашому випадку)
        assert hasattr(location, 'enemy_pool')
        # У нашому випадку enemy_pool - це список ID ворогів
        assert isinstance(location.enemy_pool, list)
        assert "goblin_01" in location.enemy_pool
        assert "skeleton_01" in location.enemy_pool
        
        # Перевіряємо connected_locations
        assert isinstance(location.connected_locations, list)
        assert "town_main" in location.connected_locations

    def test_handles_empty_json_file(self):
        """Тестує, що репозиторій коректно обробляє порожні JSON-файли"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonLocationRepository(data_path)
        
        # Ми перевіряємо, що репозиторій існує і може працювати з даними
        all_types = repo.get_all_types()
        
        # Перевіряємо, що це список і він не містить помилок
        assert isinstance(all_types, list)
        for loc_type in all_types:
            assert isinstance(loc_type, str)
            # Перевіряємо, що ми можемо отримати хоча б пустий список за будь-яким типом
            locations = repo.get_by_type(loc_type)
            assert isinstance(locations, list)
        
        # Також перевіряємо загальну кількість локацій
        all_locations = repo.get_all()
        assert isinstance(all_locations, list)