"""
Визначає типи предметів у грі.
"""
from enum import Enum

class ItemType(str, Enum):
    """Перелік можливих типів предметів."""
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    BOOTS = "boots"
    GLOVES = "gloves"
    RING = "ring"
    AMULET = "amulet"
    CONSUMABLE = "consumable"
