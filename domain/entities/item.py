from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class Item:
    """Предмет для MVP"""
    id: str
    name: str
    type: str  # weapon, armor, helmet, consumable
    rarity: str  # common, rare, epic, legendary
    level_requirement: int
    stats: Optional[Dict[str, Any]] = None  # Тепер необов'язкове поле, для предметів без статів (наприклад, зілля)
    description: str = ""
    effects: Optional[Dict[str, Any]] = None  # Додаткові ефекти для зілля та інших предметів
