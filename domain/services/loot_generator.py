"""
Сервіс для генерації нагород (луту).
"""
import random
from typing import  Dict, Any

class LootGenerator:
    """Генерує предмети та золото на основі таблиць луту."""

    def generate_loot(
        self,
        loot_table: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Генерує лут за заданою таблицею.

        :param loot_table: Словник з конфігурацією луту (золото, предмети).
        :return: Словник з генерованими нагородами.
        """
        rewards = {
            "gold": 0,
            "items": []
        }

        # Генеруємо золото
        if "gold" in loot_table:
            rewards["gold"] = random.randint(
                loot_table["gold"].get("min", 0),
                loot_table["gold"].get("max", 0)
            )

        # Генеруємо предмети
        if "items" in loot_table:
            for item_entry in loot_table["items"]:
                if random.random() < item_entry.get("probability", 0):
                    rewards["items"].append(item_entry["item_id"])

        return rewards
