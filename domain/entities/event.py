"""
Цей модуль визначає сутності для ігрових подій.
"""
from dataclasses import dataclass
from typing import  Dict, Any
from enum import Enum

class EventType(str, Enum):
    """Типи можливих подій у грі."""
    COMBAT = "combat"
    CHEST = "chest"
    TOWN_REST = "town_rest"
    NOTHING = "nothing"

@dataclass
class BaseEvent:
    """Базовий клас для всіх ігрових подій."""
    event_type: EventType
    description: str

@dataclass
class CombatEvent(BaseEvent):
    """Подія, що ініціює бій з ворогом."""
    enemy_id: str
    event_type: EventType = EventType.COMBAT

@dataclass
class ChestEvent(BaseEvent):
    """Подія, де гравець знаходить скарб."""
    loot: Dict[str, Any]
    event_type: EventType = EventType.CHEST

@dataclass
class TownRestEvent(BaseEvent):
    """Подія відпочинку в місті."""
    event_type: EventType = EventType.TOWN_REST

@dataclass
class NothingEvent(BaseEvent):
    """Подія, коли нічого не відбувається."""
    event_type: EventType = EventType.NOTHING
