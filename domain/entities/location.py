"""
Цей модуль визначає сутність Локації (Location).
"""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Location:
    """
    Сутність, що представляє ігрову локацію.
    """
    id: str
    name: str
    type: str  # town, wilderness, dungeon
    description: str
    available_actions: List[str]
    event_pool: List[Dict[str, Any]]
    enemy_pool: List[str]
    connected_locations: List[str]
