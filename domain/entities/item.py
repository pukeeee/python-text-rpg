from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Item:
    """Предмет для MVP"""
    id: str
    name: str
    type: str  # weapon, armor, helmet, consumable
    rarity: str  # common, rare, epic, legendary
    level_requirement: int
    stats: Dict[str, Any]
    description: str
