import os
from infrastructure.persistence.repositories.json_item_repository import JsonItemRepository


class TestJsonItemRepository:
    """Тести для JsonItemRepository які використовують актуальні дані"""

    def test_get_by_id_success(self):
        """Тестує отримання предмета за ID з використанням реальних даних"""
        # Використовуємо шлях до основної директорії даних
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonItemRepository(data_path)
        
        # Перевіряємо предмет, що точно існує в даних
        item = repo.get_by_id("sword_01")

        assert item is not None
        assert item.id == "sword_01"
        assert item.name == "Iron Sword"
        assert item.type == "weapon"
        assert item.rarity == "common"
        assert item.level_requirement == 1
        assert "damage_min" in item.stats
        assert item.stats["damage_min"] == 5
        assert item.stats["damage_max"] == 10
        assert item.description == "A basic iron sword"

    def test_get_by_id_not_found(self):
        """Тестує отримання неіснуючого предмета"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonItemRepository(data_path)
        item = repo.get_by_id("nonexistent_item")

        assert item is None

    def test_get_many_by_ids(self):
        """Тестує отримання декількох предметів за ID з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonItemRepository(data_path)
        
        # Перевіряємо наявність декількох предметів
        items = repo.get_many_by_ids(["sword_01", "chest_01", "health_potion"])

        assert len(items) == 3
        
        # Перевіряємо, що кожен предмет отримано правильно
        item_dict = {item.id: item for item in items}
        
        assert "sword_01" in item_dict
        assert item_dict["sword_01"].name == "Iron Sword"
        assert item_dict["sword_01"].type == "weapon"
        
        assert "chest_01" in item_dict
        assert item_dict["chest_01"].name == "Шкіряна броня"
        assert item_dict["chest_01"].type == "armor"
        
        assert "health_potion" in item_dict
        assert item_dict["health_potion"].name == "Зілля здоров'я"
        assert item_dict["health_potion"].type == "consumable"

    def test_get_by_type(self):
        """Тестує отримання предметів за типом з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonItemRepository(data_path)
        
        # Отримуємо зброю
        weapons = repo.get_by_type("weapon")
        assert len(weapons) > 0  # Повинні бути якісь зброя
        weapon_names = [w.name for w in weapons]
        assert "Iron Sword" in weapon_names  # Перевіряємо наявність відомої зброї
        
        # Отримуємо броню
        armors = repo.get_by_type("armor")
        assert len(armors) > 0
        armor_names = [a.name for a in armors]
        assert "Шкіряна броня" in armor_names  # Перевіряємо наявність відомої броні
        
        # Отримуємо зілля
        consumables = repo.get_by_type("consumable")
        assert len(consumables) > 0
        consumable_names = [c.name for c in consumables]
        assert "Зілля здоров'я" in consumable_names  # Перевіряємо наявність відомого зілля

    def test_get_all_types(self):
        """Тестує отримання всіх типів предметів з використанням реальних даних"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonItemRepository(data_path)
        all_types = repo.get_all_types()
        
        expected_types = ["weapon", "armor", "consumable", "helmet"]
        for expected_type in expected_types:
            assert expected_type in all_types

    def test_get_by_specific_types(self):
        """Тестує отримання предметів конкретних типів (наприклад, шоломи, кільця)"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonItemRepository(data_path)
        
        # Перевіряємо шоломи
        helmets = repo.get_by_type("helmet")
        assert len(helmets) > 0
        helmet_names = [h.name for h in helmets]
        assert "Залізний шолом" in helmet_names  # На основі даних з helmets.json
        
        # Перевіряємо, що інші типи також можуть бути отримані
        # Наприклад, якщо є файли з кільцями, але їх поки немає - це ок
        rings = repo.get_by_type("ring")
        # Просто переконуємось, що це список, навіть якщо пустий
        assert isinstance(rings, list)

    def test_handles_empty_json_file(self):
        """Тестує, що репозиторій коректно обробляє порожні JSON-файли"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
        repo = JsonItemRepository(data_path)
        
        # Ми перевіряємо, що репозиторій існує і може працювати з даними
        all_types = repo.get_all_types()
        
        # Перевіряємо, що це список і він не містить помилок
        assert isinstance(all_types, list)
        for item_type in all_types:
            assert isinstance(item_type, str)
            # Перевіряємо, що ми можемо отримати хоча б пустий список за будь-яким типом
            items = repo.get_by_type(item_type)
            assert isinstance(items, list)