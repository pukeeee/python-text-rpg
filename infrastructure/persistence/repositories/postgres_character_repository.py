"""
Цей модуль містить конкретну реалізацію репозиторію для персонажів,
використовуючи PostgreSQL як сховище даних. Він реалізує інтерфейс ICharacterRepository,
визначений у доменному шарі, і слугує адаптером між доменними сутностями та моделями БД.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
import hashlib

from domain.entities.character import Character
from domain.repositories.character_repository import ICharacterRepository
from infrastructure.persistence.database.models import (
    CharacterModel, EquipmentModel, InventoryModel, StatsCacheModel
)
from domain.value_objects.stats import BaseStats


class PostgresCharacterRepository(ICharacterRepository):
    """
    Репозиторій для персонажів, що працює з базою даних PostgreSQL через SQLAlchemy.
    """
    def __init__(self, session: Session):
        # Репозиторій отримує готову сесію ззовні (Dependency Injection).
        # Він не керує її створенням чи закриттям.
        self.session = session

    def save(self, character: Character) -> None:
        """Зберігає або оновлює повний стан персонажа в базі даних."""
        # 1. Знайти існуючий запис у БД або підготувати новий.
        db_character = self.session.query(CharacterModel).filter_by(
            id=UUID(character.id)
        ).first()

        if db_character is None:
            # Якщо персонажа немає, створюємо нову модель і додаємо її в сесію.
            db_character = CharacterModel(id=UUID(character.id))
            self.session.add(db_character)

        # 2. Оновити поля моделі даними з доменної сутності.
        db_character.telegram_user_id = character.telegram_user_id
        db_character.name = character.name
        db_character.level = character.level
        db_character.experience = character.experience
        db_character.strength = character.base_stats.strength
        db_character.dexterity = character.base_stats.dexterity
        db_character.intelligence = character.base_stats.intelligence
        db_character.base_health = character.base_stats.base_health
        db_character.base_mana = character.base_stats.base_mana
        db_character.current_health = character.current_health
        db_character.current_mana = character.current_mana
        db_character.location_id = character.location_id

        # 3. Окремо обробити пов'язані дані: екіпіровку та інвентар.
        self._save_equipment(character, db_character)
        self._save_inventory(character)

    def get(self, character_id: str) -> Optional[Character]:
        """Завантажує персонажа за ID, жадібно підтягуючи всі пов'язані дані."""
        # joinedload() каже SQLAlchemy завантажити пов'язані моделі (equipment, inventory і т.д.)
        # одним або кількома додатковими запитами, що ефективніше, ніж ліниве завантаження.
        db_character = self.session.query(CharacterModel).options(
            joinedload(CharacterModel.equipment),
            joinedload(CharacterModel.inventory),
            joinedload(CharacterModel.stats_cache),
            joinedload(CharacterModel.combat_state)
        ).filter_by(id=UUID(character_id)).first()

        if db_character is None:
            return None

        # Перетворюємо модель БД на доменну сутність перед поверненням.
        return self._to_domain(db_character)

    def get_by_telegram_user_id(self, telegram_user_id: int) -> Optional[Character]:
        """Отримання персонажа за унікальним ідентифікатором Telegram."""
        db_character = self.session.query(CharacterModel).options(
            joinedload(CharacterModel.equipment),
            joinedload(CharacterModel.inventory),
            joinedload(CharacterModel.stats_cache),
            joinedload(CharacterModel.combat_state)
        ).filter_by(telegram_user_id=telegram_user_id).first()

        if db_character is None:
            return None

        return self._to_domain(db_character)

    def delete(self, character_id: str) -> None:
        """Видаляє персонажа з БД. Каскадне видалення налаштовано в моделях."""
        self.session.query(CharacterModel).filter_by(
            id=UUID(character_id)
        ).delete()

    def save_stats_cache(self, character_id: str, stats: Dict[str, Any], equipment_items: List[str]) -> None:
        """Зберігає кеш розрахованих характеристик персонажа."""
        equipment_hash = self._calculate_equipment_hash(equipment_items)
        char_uuid = UUID(character_id)

        # Шукаємо кеш, що належить конкретному персонажу.
        cache = self.session.query(StatsCacheModel).filter_by(
            character_id=char_uuid
        ).first()

        if cache is None:
            cache = StatsCacheModel(character_id=char_uuid)
            self.session.add(cache)

        # Оновлюємо дані кешу.
        cache.total_health = stats['max_health']
        cache.total_mana = stats['max_mana']
        cache.armor = stats['armor']
        cache.evasion = stats['evasion']
        cache.energy_shield = stats['energy_shield']
        cache.damage_min = stats['damage_min']
        cache.damage_max = stats['damage_max']
        cache.accuracy = stats['accuracy']
        # Конвертуємо у Decimal для збереження в полях Numeric для точності.
        cache.critical_chance = Decimal(str(stats['critical_chance']))
        cache.critical_multiplier = Decimal(str(stats['critical_multiplier']))
        cache.attack_speed = Decimal(str(stats['attack_speed']))
        cache.equipment_hash = equipment_hash
        cache.calculated_at = datetime.now(timezone.utc)

    def get_stats_cache(self, character_id: str, equipment_items: List[str]) -> Optional[Dict[str, Any]]:
        """Отримання кеша статистики, якщо він актуальний."""
        cache = self.session.query(StatsCacheModel).filter_by(
            character_id=UUID(character_id)
        ).first()

        if cache is None:
            return None # Немає кешу.

        # Перевірка актуальності кешу: порівнюємо хеші поточної та кешованої екіпіровки.
        current_hash = self._calculate_equipment_hash(equipment_items)
        if cache.equipment_hash != current_hash:
            return None # Кеш застарів.

        # Повертаємо дані кешу у вигляді словника.
        return {
            'max_health': cache.total_health,
            'max_mana': cache.total_mana,
            'armor': cache.armor,
            'evasion': cache.evasion,
            'energy_shield': cache.energy_shield,
            'damage_min': cache.damage_min,
            'damage_max': cache.damage_max,
            'accuracy': cache.accuracy,
            'critical_chance': float(cache.critical_chance),
            'critical_multiplier': float(cache.critical_multiplier),
            'attack_speed': float(cache.attack_speed)
        }

    def _save_equipment(self, character: Character, db_character: CharacterModel) -> None:
        """Допоміжний метод для збереження екіпіровки."""
        # Використовуємо існуючий зв'язок, якщо він вже завантажений.
        equipment = db_character.equipment
        if equipment is None:
            equipment = EquipmentModel(character_id=UUID(character.id))
            self.session.add(equipment)

        # Оновлюємо кожен слот.
        equipment.weapon = character.equipped_items.get('weapon')
        equipment.armor = character.equipped_items.get('armor')
        equipment.helmet = character.equipped_items.get('helmet')
        equipment.boots = character.equipped_items.get('boots')
        equipment.gloves = character.equipped_items.get('gloves')
        equipment.ring_1 = character.equipped_items.get('ring_1')
        equipment.ring_2 = character.equipped_items.get('ring_2')
        equipment.amulet = character.equipped_items.get('amulet')

    def _save_inventory(self, character: Character) -> None:
        """
        Допоміжний метод для збереження інвентаря.
        Стратегія "видалити і вставити": проста, але може бути неефективною для великих інвентарів.
        Альтернатива - складніша логіка для порівняння та оновлення/додавання/видалення окремих записів.
        """
        # 1. Повністю видаляємо старий інвентар персонажа.
        self.session.query(InventoryModel).filter_by(
            character_id=UUID(character.id)
        ).delete()

        # 2. Рахуємо кількість кожного унікального предмета в доменному об'єкті.
        item_counts = {}
        for item_id in character.inventory:
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        # 3. Створюємо нові записи в БД для кожного унікального предмета.
        for item_id, quantity in item_counts.items():
            inventory_item = InventoryModel(
                character_id=UUID(character.id),
                item_id=item_id,
                quantity=quantity
            )
            self.session.add(inventory_item)

    def _to_domain(self, db_character: CharacterModel) -> Character:
        """
        Перетворює модель SQLAlchemy (дані з БД) на доменну сутність Character.
        Це ключовий патерн Чистої Архітектури: внутрішні шари (домен)
        не повинні знати про деталі зовнішніх шарів (база даних).
        """
        base_stats = BaseStats(
            strength=db_character.strength,
            dexterity=db_character.dexterity,
            intelligence=db_character.intelligence,
            base_health=db_character.base_health,
            base_mana=db_character.base_mana
        )

        equipped_items = {}
        if db_character.equipment is not None:
            equipped_items = {
                'weapon': db_character.equipment.weapon,
                'armor': db_character.equipment.armor,
                'helmet': db_character.equipment.helmet,
                'boots': db_character.equipment.boots,
                'gloves': db_character.equipment.gloves,
                'ring_1': db_character.equipment.ring_1,
                'ring_2': db_character.equipment.ring_2,
                'amulet': db_character.equipment.amulet
            }

        inventory = []
        if db_character.inventory:
            for inv_item in db_character.inventory:
                inventory.extend([inv_item.item_id] * inv_item.quantity)

        combat_state = None
        if db_character.combat_state is not None:
            combat_state = {
                'enemy_id': db_character.combat_state.enemy_id,
                'enemy_current_health': db_character.combat_state.enemy_current_health,
                'enemy_max_health': db_character.combat_state.enemy_max_health,
                'turn': db_character.combat_state.turn_number
            }

        # Створюємо чистий доменний об'єкт з даних, отриманих з БД.
        return Character(
            id=str(db_character.id),
            telegram_user_id=db_character.telegram_user_id,
            name=db_character.name,
            level=db_character.level,
            experience=db_character.experience,
            base_stats=base_stats,
            current_health=db_character.current_health,
            current_mana=db_character.current_mana,
            equipped_items=equipped_items,
            inventory=inventory,
            location_id=db_character.location_id,
            combat_state=combat_state
        )

    def _calculate_equipment_hash(self, equipment_items: List[str]) -> str:
        """Розрахунок хешу екіпіровки для інвалідації кешу."""
        # Сортуємо ID предметів, щоб порядок не впливав на хеш.
        equipment_str = ','.join(sorted(equipment_items))
        return hashlib.sha256(equipment_str.encode()).hexdigest()