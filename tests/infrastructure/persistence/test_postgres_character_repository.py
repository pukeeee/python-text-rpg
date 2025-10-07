# tests/infrastructure/persistence/test_postgres_character_repository.py
"""
Інтеграційні тести для PostgresCharacterRepository.
"""
from uuid import uuid4

from domain.entities.character import Character
from domain.value_objects.stats import BaseStats
from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository


class TestPostgresCharacterRepository:
    """Групує тести для репозиторію персонажів."""

    def test_save_and_get_character(self, db_session):
        """Перевіряє базовий функціонал збереження та отримання персонажа."""
        # 1. Підготовка даних
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        base_stats = BaseStats(strength=12, dexterity=14, intelligence=10, base_health=110, base_mana=55)

        original_character = Character(
            id=character_id,
            telegram_user_id=12345,
            name="Test_Hero",
            level=5,
            experience=1500,
            base_stats=base_stats,
            current_health=100,
            current_mana=50,
            location_id="test_location",
            equipped_items={'weapon': 'sword_1'},
            inventory=['potion_1', 'potion_1']
        )

        # 2. Дія: Зберігаємо персонажа
        repo.save(original_character)
        db_session.commit() # Потрібен коміт, щоб дані збереглися в транзакції

        # 3. Перевірка: Отримуємо персонажа з БД
        retrieved_character = repo.get(character_id)

        # 4. Твердження: Перевіряємо, що отримані дані відповідають оригіналу
        assert retrieved_character is not None
        assert retrieved_character.id == original_character.id
        assert retrieved_character.name == "Test_Hero"
        assert retrieved_character.level == 5
        assert retrieved_character.telegram_user_id == 12345
        assert retrieved_character.base_stats.strength == 12
        assert retrieved_character.current_health == 100
        assert retrieved_character.location_id == "test_location"
        assert retrieved_character.equipped_items.get('weapon') == 'sword_1'
        assert 'potion_1' in retrieved_character.inventory
        assert retrieved_character.inventory.count('potion_1') == 2

    def test_update_character(self, db_session):
        """Перевіряє, що метод save() коректно оновлює існуючого персонажа."""
        # 1. Підготовка: Створюємо і зберігаємо персонажа
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        original_character = Character(
            id=character_id, telegram_user_id=23456, name="Old Name", level=1, experience=100,
            base_stats=BaseStats(10, 10, 10, 100, 50), current_health=100, current_mana=50,
            location_id="start", equipped_items={}, inventory=[]
        )
        repo.save(original_character)
        db_session.commit()

        # 2. Дія: Змінюємо дані та зберігаємо ще раз
        original_character.name = "New Name"
        original_character.level = 2
        repo.save(original_character)
        db_session.commit()

        # 3. Перевірка: Отримуємо персонажа і перевіряємо оновлені поля
        updated_character = repo.get(character_id)
        assert updated_character is not None
        assert updated_character.name == "New Name"
        assert updated_character.level == 2

    def test_get_non_existent_character(self, db_session):
        """Перевіряє, що get() повертає None для неіснуючого ID."""
        repo = PostgresCharacterRepository(db_session)
        non_existent_id = str(uuid4())
        character = repo.get(non_existent_id)
        assert character is None

    def test_get_by_telegram_user_id(self, db_session):
        """Перевіряє отримання персонажа за ID користувача Telegram."""
        # 1. Підготовка
        repo = PostgresCharacterRepository(db_session)
        telegram_id = 34567
        character = Character(
            id=str(uuid4()), telegram_user_id=telegram_id, name="TG_User", level=3, experience=300,
            base_stats=BaseStats(10, 10, 10, 100, 50), current_health=100, current_mana=50,
            location_id="start", equipped_items={}, inventory=[]
        )
        repo.save(character)
        db_session.commit()

        # 2. Дія та Перевірка
        retrieved_character = repo.get_by_telegram_user_id(telegram_id)
        assert retrieved_character is not None
        assert retrieved_character.telegram_user_id == telegram_id
        assert retrieved_character.name == "TG_User"

        # 3. Перевірка неіснуючого ID
        non_existent_tg_id = 99999
        character = repo.get_by_telegram_user_id(non_existent_tg_id)
        assert character is None

    def test_delete_character(self, db_session):
        """Перевіряє, що персонаж коректно видаляється."""
        # 1. Підготовка
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        character = Character(
            id=character_id, telegram_user_id=45678, name="ToDelete", level=1, experience=0,
            base_stats=BaseStats(10, 10, 10, 100, 50), current_health=100, current_mana=50,
            location_id="limbo", equipped_items={}, inventory=[]
        )
        repo.save(character)
        db_session.commit()

        # Переконуємось, що персонаж існує
        assert repo.get(character_id) is not None

        # 2. Дія
        repo.delete(character_id)
        db_session.commit()

        # 3. Перевірка
        assert repo.get(character_id) is None

    def test_stats_cache_save_and_get(self, db_session):
        """Перевіряє збереження та отримання актуального кешу статистики."""
        # 1. Підготовка
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        character = Character(id=character_id, telegram_user_id=56789, name="CacheMan", level=10, experience=10000,
                              base_stats=BaseStats(20, 20, 20, 200, 100), current_health=200, current_mana=100,
                              location_id="cache_land", equipped_items={}, inventory=[])
        repo.save(character)
        db_session.commit()

        stats_to_cache = {
            'max_health': 300, 'max_mana': 150, 'armor': 500, 'evasion': 400, 'energy_shield': 100,
            'damage_min': 50, 'damage_max': 100, 'accuracy': 800, 'critical_chance': 0.25,
            'critical_multiplier': 2.0, 'attack_speed': 1.5
        }
        equipment = ['sword_of_caching', 'shield_of_validation']

        # 2. Дія: Зберігаємо кеш
        repo.save_stats_cache(character_id, stats_to_cache, equipment)
        db_session.commit()

        # 3. Перевірка: Отримуємо кеш з тією ж екіпіровкою
        retrieved_cache = repo.get_stats_cache(character_id, equipment)
        assert retrieved_cache is not None
        assert retrieved_cache['max_health'] == 300
        assert retrieved_cache['critical_chance'] == 0.25

    def test_get_stale_stats_cache(self, db_session):
        """Перевіряє, що get_stats_cache повертає None, якщо кеш застарів (екіпіровка змінилась)."""
        # 1. Підготовка: Зберігаємо персонажа і кеш
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        character = Character(id=character_id, telegram_user_id=67890, name="StaleMan", level=1, experience=0,
                              base_stats=BaseStats(1, 1, 1, 1, 1), current_health=1, current_mana=1,
                              location_id="stale_place", equipped_items={}, inventory=[])
        repo.save(character)
        db_session.commit()

        stats_to_cache = {'max_health': 10, 'max_mana': 10, 'armor': 10, 'evasion': 10, 'energy_shield': 10,
                          'damage_min': 1, 'damage_max': 2, 'accuracy': 100, 'critical_chance': 0.05,
                          'critical_multiplier': 1.5, 'attack_speed': 1.0}
        old_equipment = ['rusty_sword']
        repo.save_stats_cache(character_id, stats_to_cache, old_equipment)
        db_session.commit()

        # 2. Дія: Намагаємось отримати кеш з новою екіпіровкою
        new_equipment = ['shiny_sword']
        retrieved_cache = repo.get_stats_cache(character_id, new_equipment)

        # 3. Перевірка
        assert retrieved_cache is None

    def test_inventory_update(self, db_session):
        """Перевіряє, що оновлення інвентаря працює коректно (стратегія delete-insert)."""
        # 1. Підготовка: Створюємо персонажа з початковим інвентарем
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        character = Character(
            id=character_id, telegram_user_id=78901, name="Pack Rat", level=5, experience=1000,
            base_stats=BaseStats(10, 10, 10, 100, 50), inventory=['apple', 'cheese', 'apple']
        )
        repo.save(character)
        db_session.commit()

        # Перевіряємо початковий стан
        retrieved = repo.get(character_id)
        assert retrieved is not None
        assert sorted(retrieved.inventory) == ['apple', 'apple', 'cheese']

        # 2. Дія: Оновлюємо інвентар
        retrieved.inventory = ['cheese', 'bread']
        repo.save(retrieved)
        db_session.commit()

        # 3. Перевірка: Отримуємо персонажа і перевіряємо новий інвентар
        final_character = repo.get(character_id)
        assert final_character is not None
        assert sorted(final_character.inventory) == ['bread', 'cheese']
        assert 'apple' not in final_character.inventory

    def test_calculate_equipment_hash_logic(self, db_session):
        """Перевіряє логіку розрахунку хешу екіпіровки.

        Це юніт-тест для внутрішнього методу, але він важливий для логіки кешування.
        """
        repo = PostgresCharacterRepository(db_session) # Сесія тут не використовується

        equipment1 = ['sword', 'shield', 'helmet']
        equipment2 = ['helmet', 'sword', 'shield'] # Той самий набір, інший порядок
        equipment3 = ['sword', 'shield'] # Інший набір

        hash1 = repo._calculate_equipment_hash(equipment1)
        hash2 = repo._calculate_equipment_hash(equipment2)
        hash3 = repo._calculate_equipment_hash(equipment3)

        # Хеші для однакових наборів (незалежно від порядку) мають бути однаковими
        assert hash1 == hash2
        # Хеші для різних наборів мають бути різними
        assert hash1 != hash3
        # Перевірка, що хеш не порожній
        assert isinstance(hash1, str) and len(hash1) == 64

    def test_get_character_with_no_equipment(self, db_session):
        """Перевіряє, що отримання персонажа без екіпіровки працює коректно."""
        # 1. Підготовка: Створюємо персонажа без екіпіровки
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        base_stats = BaseStats(strength=12, dexterity=14, intelligence=10, base_health=110, base_mana=55)

        character = Character(
            id=character_id,
            telegram_user_id=12345,
            name="NoEquipmentHero",
            level=5,
            experience=1500,
            base_stats=base_stats,
            current_health=100,
            current_mana=50,
            location_id="test_location",
            equipped_items={},  # Пустий словник екіпіровки
            inventory=['potion_1']
        )

        repo.save(character)
        db_session.commit()

        # 2. Дія: Отримуємо персонажа
        retrieved_character = repo.get(character_id)

        # 3. Перевірка: Екіпіровка повинна мати всі слоти з None
        assert retrieved_character is not None
        # Перевіряємо, що всі значення в словнику екіпіровки дорівнюють None
        for slot_value in retrieved_character.equipped_items.values():
            assert slot_value is None

    def test_get_character_with_no_inventory(self, db_session):
        """Перевіряє, що отримання персонажа без інвентарю працює коректно."""
        # 1. Підготовка: Створюємо персонажа без інвентарю
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        base_stats = BaseStats(strength=10, dexterity=10, intelligence=10, base_health=100, base_mana=50)

        character = Character(
            id=character_id,
            telegram_user_id=23456,
            name="NoInventoryHero",
            level=1,
            experience=0,
            base_stats=base_stats,
            current_health=100,
            current_mana=50,
            location_id="test_location",
            equipped_items={'weapon': 'basic_sword'},
            inventory=[]  # Пустий список інвентарю
        )

        repo.save(character)
        db_session.commit()

        # 2. Дія: Отримуємо персонажа
        retrieved_character = repo.get(character_id)

        # 3. Перевірка: Інвентар повинен бути порожнім списком
        assert retrieved_character is not None
        assert retrieved_character.inventory == []

    def test_save_character_with_empty_equipment_slots(self, db_session):
        """Перевіряє збереження персонажа з частково заповненою екіпіровкою."""
        # 1. Підготовка: Створюємо персонажа з частково заповненою екіпіровкою
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())
        base_stats = BaseStats(strength=15, dexterity=15, intelligence=15, base_health=150, base_mana=75)

        # Встановлюємо тільки збрю та обладунок, інші слоти залишаємо порожніми
        character = Character(
            id=character_id,
            telegram_user_id=34567,
            name="PartialEquipmentHero",
            level=3,
            experience=500,
            base_stats=base_stats,
            current_health=150,
            current_mana=75,
            location_id="test_location",
            equipped_items={
                'weapon': 'sword_of_power',
                'armor': 'light_armor'
                # Інші слоти відсутні
            },
            inventory=['potion_1', 'potion_2']
        )

        repo.save(character)
        db_session.commit()

        # 2. Дія: Отримуємо персонажа
        retrieved_character = repo.get(character_id)

        # 3. Перевірка: Перевіряємо, що лише встановлені слоти збереглися правильно
        assert retrieved_character is not None
        assert retrieved_character.equipped_items.get('weapon') == 'sword_of_power'
        assert retrieved_character.equipped_items.get('armor') == 'light_armor'
        # Інші слоти мають бути None
        assert retrieved_character.equipped_items.get('helmet') is None
        assert retrieved_character.equipped_items.get('boots') is None
        assert retrieved_character.equipped_items.get('gloves') is None
        assert retrieved_character.equipped_items.get('ring_1') is None
        assert retrieved_character.equipped_items.get('ring_2') is None
        assert retrieved_character.equipped_items.get('amulet') is None

    def test_to_domain_method_with_no_related_data(self, db_session):
        """Перевіряє внутрішній метод _to_domain з відсутністю пов'язаних даних."""
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())

        # Створюємо персонажа з пустими значеннями для пов'язаних моделей
        character = Character(
            id=character_id,
            telegram_user_id=45678,
            name="MinimalHero",
            level=1,
            experience=0,
            base_stats=BaseStats(strength=10, dexterity=10, intelligence=10, base_health=100, base_mana=50),
            current_health=100,
            current_mana=50,
            location_id="test_location",
            equipped_items={},
            inventory=[]
        )

        repo.save(character)  # Це збереже персонажа і порожню екіпіровку та інвентар
        db_session.commit()

        # Отримуємо персонажа з бази даних для перевірки
        retrieved_character = repo.get(character_id)

        # Перевіряємо, що метод _to_domain правильно обробляє відсутність даних
        assert retrieved_character is not None
        assert retrieved_character.name == "MinimalHero"
        # Перевіряємо, що всі значення в словнику екіпіровки дорівнюють None
        for slot_value in retrieved_character.equipped_items.values():
            assert slot_value is None
        assert retrieved_character.inventory == []
        # combat_state має бути None, якщо пов'язаний об'єкт не створений
        # (це відбувається автоматично, оскільки ми не створювали combat_state в моделі)

    def test_save_empty_inventory(self, db_session):
        """Перевіряє збереження персонажа з порожнім інвентарем."""
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())

        # Створюємо персонажа з порожнім інвентарем
        character = Character(
            id=character_id,
            telegram_user_id=56789,
            name="EmptyInventoryHero",
            level=2,
            experience=100,
            base_stats=BaseStats(12, 12, 12, 120, 60),
            current_health=120,
            current_mana=60,
            location_id="empty_shop",
            equipped_items={'weapon': 'training_sword'},
            inventory=[]  # Порожній інвентар
        )

        repo.save(character)
        db_session.commit()

        # Отримуємо персонажа
        retrieved_character = repo.get(character_id)

        # Перевіряємо, що інвентар дійсно порожній
        assert retrieved_character is not None
        assert retrieved_character.inventory == []

        # Перевіряємо, що екіпіровка збереглася
        assert retrieved_character.equipped_items.get('weapon') == 'training_sword'

    def test_get_stats_cache_when_no_cache_exists(self, db_session):
        """Перевіряє, що get_stats_cache повертає None, коли кешу немає в БД."""
        repo = PostgresCharacterRepository(db_session)
        character_id = str(uuid4())

        # Створюємо та зберігаємо персонажа, але не зберігаємо кеш статистики
        character = Character(
            id=character_id,
            telegram_user_id=67890,
            name="NoCacheHero",
            level=1,
            experience=0,
            base_stats=BaseStats(10, 10, 10, 100, 50),
            current_health=100,
            current_mana=50,
            location_id="cacheless_zone",
            equipped_items={},
            inventory=[]
        )

        repo.save(character)
        db_session.commit()

        # Перевіряємо, що кеш статистики не існує
        equipment = ['old_shield']
        cached_stats = repo.get_stats_cache(character_id, equipment)

        # Кеш не існує, має повертати None
        assert cached_stats is None
