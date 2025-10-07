from domain.entities.character import Character
from domain.entities.enemy import Enemy
from domain.value_objects.stats import Stats
from domain.value_objects.enemy_stats import EnemyStats
from domain.repositories.item_repository import IItemRepository

class StatsCalculator:
    """Сервіс для розрахунку підсумкових характеристик персонажа та ворогів."""

    def __init__(self, item_repository: IItemRepository):
        self.item_repository = item_repository

    def calculate_enemy_stats(self, enemy: Enemy, character_level: int) -> EnemyStats:
        """
        Розраховує характеристики ворога. В майбутньому може включати логіку скейлінгу.
        Для MVP просто повертає базові характеристики.
        """
        # TODO: Додати логіку скейлінгу характеристик ворога від рівня персонажа
        return enemy.stats

    def calculate_total_stats(self, character: Character) -> Stats:
        """
        Розраховує всі характеристики з урахуванням базових статів та екіпіровки.
        """
        # Отримуємо предмети, що екіпіровані
        equipped_item_ids = [item_id for item_id in character.equipped_items.values() if item_id]
        equipped_items = self.item_repository.get_many_by_ids(equipped_item_ids)

        # Базові характеристики
        strength = character.base_stats.strength
        dexterity = character.base_stats.dexterity
        intelligence = character.base_stats.intelligence

        # Модифікатори від предметів
        item_strength = sum(item.stats.get('strength', 0) for item in equipped_items)
        item_dexterity = sum(item.stats.get('dexterity', 0) for item in equipped_items)
        item_intelligence = sum(item.stats.get('intelligence', 0) for item in equipped_items)
        
        total_strength = strength + item_strength
        total_dexterity = dexterity + item_dexterity
        total_intelligence = intelligence + item_intelligence

        # Здоров'я та мана
        base_health = character.base_stats.base_health
        item_health = sum(item.stats.get('health', 0) for item in equipped_items)
        max_health = base_health + (total_strength * 5) + item_health

        base_mana = character.base_stats.base_mana
        item_mana = sum(item.stats.get('mana', 0) for item in equipped_items)
        max_mana = base_mana + (total_intelligence * 3) + item_mana

        # Захист
        item_armor = sum(item.stats.get('armor', 0) for item in equipped_items)
        armor = item_armor
        
        item_evasion = sum(item.stats.get('evasion', 0) for item in equipped_items)
        evasion = (total_dexterity * 2) + item_evasion

        item_energy_shield = sum(item.stats.get('energy_shield', 0) for item in equipped_items)
        energy_shield = (total_intelligence * 2) + item_energy_shield

        # Атака
        weapon = next((item for item in equipped_items if item.type == 'weapon'), None)
        if weapon:
            damage_min = weapon.stats.get('damage_min', 1) + int(total_strength * 0.5)
            damage_max = weapon.stats.get('damage_max', 2) + int(total_strength * 1.0)
            accuracy = weapon.stats.get('accuracy', 85) + (total_dexterity * 2)
            critical_chance = weapon.stats.get('critical_chance', 5.0) + (total_dexterity * 0.5)
            critical_multiplier = weapon.stats.get('critical_multiplier', 1.5)
            attack_speed = weapon.stats.get('attack_speed', 1.0) * (1 + total_dexterity * 0.01)
        else: # Рукопашний бій
            damage_min = 1 + int(total_strength * 0.5)
            damage_max = 3 + int(total_strength * 1.0)
            accuracy = 85 + (total_dexterity * 2)
            critical_chance = 5.0 + (total_dexterity * 0.5)
            critical_multiplier = 1.5
            attack_speed = 1.0 + (total_dexterity * 0.01)

        return Stats(
            strength=total_strength,
            dexterity=total_dexterity,
            intelligence=total_intelligence,
            health=character.current_health,
            max_health=max_health,
            mana=character.current_mana,
            max_mana=max_mana,
            armor=armor,
            evasion=evasion,
            energy_shield=energy_shield,
            damage_min=damage_min,
            damage_max=damage_max,
            accuracy=accuracy,
            critical_chance=critical_chance,
            critical_multiplier=critical_multiplier,
            attack_speed=attack_speed
        )
