"""
Виправлена реалізація репозиторію персонажів з правильною обробкою combat_state.
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
    CharacterModel, EquipmentModel, InventoryModel, StatsCacheModel, CombatStateModel
)
from domain.value_objects.stats import BaseStats


class PostgresCharacterRepository(ICharacterRepository):
    """
    Репозиторій для персонажів з правильною обробкою всіх зв'язків.
    """
    def __init__(self, session: Session):
        self.session = session

    def save(self, character: Character) -> None:
        """Зберігає або оновлює повний стан персонажа в базі даних."""
        # 1. Основна модель персонажа
        db_character = self.session.query(CharacterModel).filter_by(
            id=UUID(character.id)
        ).first()

        if db_character is None:
            db_character = CharacterModel(id=UUID(character.id))
            self.session.add(db_character)

        # 2. Оновлення полів
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
        db_character.updated_at = datetime.now(timezone.utc)
        db_character.last_activity_at = datetime.now(timezone.utc)

        # 3. Збереження пов'язаних даних
        self._save_equipment(character, db_character)
        self._save_inventory(character)
        self._save_combat_state(character, db_character)

    def get(self, character_id: str) -> Optional[Character]:
        """Завантажує персонажа за ID."""
        db_character = self.session.query(CharacterModel).options(
            joinedload(CharacterModel.equipment),
            joinedload(CharacterModel.inventory),
            joinedload(CharacterModel.stats_cache),
            joinedload(CharacterModel.combat_state)
        ).filter_by(id=UUID(character_id)).first()

        if db_character is None:
            return None

        return self._to_domain(db_character)

    def get_by_telegram_user_id(self, telegram_user_id: int) -> Optional[Character]:
        """Отримання персонажа за Telegram ID."""
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
        """Видаляє персонажа."""
        self.session.query(CharacterModel).filter_by(
            id=UUID(character_id)
        ).delete()

    def save_stats_cache(self, character_id: str, stats: Dict[str, Any], equipment_items: List[str]) -> None:
        """Зберігає кеш характеристик."""
        equipment_hash = self._calculate_equipment_hash(equipment_items)
        char_uuid = UUID(character_id)

        cache = self.session.query(StatsCacheModel).filter_by(
            character_id=char_uuid
        ).first()

        if cache is None:
            cache = StatsCacheModel(character_id=char_uuid)
            self.session.add(cache)

        cache.total_health = stats['max_health']
        cache.total_mana = stats['max_mana']
        cache.armor = stats['armor']
        cache.evasion = stats['evasion']
        cache.energy_shield = stats['energy_shield']
        cache.damage_min = stats['damage_min']
        cache.damage_max = stats['damage_max']
        cache.accuracy = stats['accuracy']
        cache.critical_chance = Decimal(str(stats['critical_chance']))
        cache.critical_multiplier = Decimal(str(stats['critical_multiplier']))
        cache.attack_speed = Decimal(str(stats['attack_speed']))
        cache.equipment_hash = equipment_hash
        cache.calculated_at = datetime.now(timezone.utc)

    def get_stats_cache(self, character_id: str, equipment_items: List[str]) -> Optional[Dict[str, Any]]:
        """Отримання кешу характеристик."""
        cache = self.session.query(StatsCacheModel).filter_by(
            character_id=UUID(character_id)
        ).first()

        if cache is None:
            return None

        current_hash = self._calculate_equipment_hash(equipment_items)
        if cache.equipment_hash != current_hash:
            return None

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
        """Зберігає екіпіровку."""
        equipment = db_character.equipment
        if equipment is None:
            equipment = EquipmentModel(character_id=UUID(character.id))
            self.session.add(equipment)

        equipment.weapon = character.equipped_items.get('weapon')
        equipment.armor = character.equipped_items.get('armor')
        equipment.helmet = character.equipped_items.get('helmet')
        equipment.boots = character.equipped_items.get('boots')
        equipment.gloves = character.equipped_items.get('gloves')
        equipment.ring_1 = character.equipped_items.get('ring_1')
        equipment.ring_2 = character.equipped_items.get('ring_2')
        equipment.amulet = character.equipped_items.get('amulet')
        equipment.updated_at = datetime.now(timezone.utc)

    def _save_inventory(self, character: Character) -> None:
        """Зберігає інвентар."""
        # Видаляємо старий інвентар
        self.session.query(InventoryModel).filter_by(
            character_id=UUID(character.id)
        ).delete()

        # Підраховуємо кількість предметів
        item_counts = {}
        for item_id in character.inventory:
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        # Створюємо нові записи
        for item_id, quantity in item_counts.items():
            inventory_item = InventoryModel(
                character_id=UUID(character.id),
                item_id=item_id,
                quantity=quantity,
                acquired_at=datetime.now(timezone.utc)
            )
            self.session.add(inventory_item)

    def _save_combat_state(self, character: Character, db_character: CharacterModel) -> None:
        """Зберігає стан бою. ВИПРАВЛЕНА ВЕРСІЯ."""
        # Спочатку видаляємо старий combat_state якщо він є
        existing_combat = self.session.query(CombatStateModel).filter_by(
            character_id=UUID(character.id)
        ).first()

        if character.combat_state is None:
            # Якщо бою немає, видаляємо запис
            if existing_combat:
                self.session.delete(existing_combat)
        else:
            # Якщо бій є, створюємо або оновлюємо
            if existing_combat is None:
                existing_combat = CombatStateModel(character_id=UUID(character.id))
                self.session.add(existing_combat)

            # Оновлюємо дані бою
            existing_combat.enemy_id = character.combat_state['enemy_id']
            existing_combat.enemy_level = character.combat_state.get('enemy_level', 1)
            existing_combat.enemy_current_health = character.combat_state['enemy_current_health']
            existing_combat.enemy_max_health = character.combat_state.get(
                'enemy_max_health',
                character.combat_state['enemy_current_health']
            )
            existing_combat.turn_number = character.combat_state.get('turn', 0)

    def _to_domain(self, db_character: CharacterModel) -> Character:
        """Конвертує модель БД в доменну сутність."""
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
                'combat_id': f"combat_{db_character.id}_{db_character.combat_state.enemy_id}",
                'enemy_id': db_character.combat_state.enemy_id,
                'enemy_level': db_character.combat_state.enemy_level,
                'enemy_current_health': db_character.combat_state.enemy_current_health,
                'enemy_max_health': db_character.combat_state.enemy_max_health,
                'turn': db_character.combat_state.turn_number
            }

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
        """Розрахунок хешу екіпіровки."""
        equipment_str = ','.join(sorted(equipment_items))
        return hashlib.sha256(equipment_str.encode()).hexdigest()
