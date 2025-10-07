from domain.entities.character import Character
from domain.value_objects.stats import Stats

class StatsCalculator:
    """Сервис для расчёта итоговых характеристик персонажа"""

    def calculate_total_stats(self, character: Character) -> Stats:
        """
        Рассчитывает все характеристики с учётом базовых статов и экипировки

        Для MVP - упрощённые формулы, потом добавим предметы
        """
        # Базовые характеристики
        strength = character.base_stats.strength
        dexterity = character.base_stats.dexterity
        intelligence = character.base_stats.intelligence

        # Здоровье и мана
        max_health = character.base_stats.base_health + (strength * 5)
        max_mana = character.base_stats.base_mana + (intelligence * 3)

        # Защита (временно без предметов)
        armor = 0  # Будет из экипировки
        evasion = dexterity * 2  # Базовое уклонение
        energy_shield = intelligence * 2

        # Атака (временно базовая, без оружия)
        damage_min = 1 + int(strength * 0.5)
        damage_max = 3 + int(strength * 1.0)
        accuracy = 85 + (dexterity * 2)

        # Криты
        critical_chance = 5.0 + (dexterity * 0.5)
        critical_multiplier = 1.5
        attack_speed = 1.0 + (dexterity * 0.01)

        return Stats(
            strength=strength,
            dexterity=dexterity,
            intelligence=intelligence,
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
