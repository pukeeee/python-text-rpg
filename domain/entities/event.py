"""
Цей модуль визначає сутності для ігрових подій.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
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
    description: str
    event_type: EventType

@dataclass
class CombatEvent(BaseEvent):
    """Подія, що ініціює бій з ворогом."""
    enemy_id: str
    event_type: EventType = field(default=EventType.COMBAT, init=False)

@dataclass
class ChestEvent(BaseEvent):
    """Подія, де гравець знаходить скарб."""
    loot: Dict[str, Any]
    event_type: EventType = field(default=EventType.CHEST, init=False)

@dataclass
class TownRestEvent(BaseEvent):
    """Подія відпочинку в місті."""
    event_type: EventType = field(default=EventType.TOWN_REST, init=False)

@dataclass
class NothingEvent(BaseEvent):
    """Подія, коли нічого не відбувається."""
    event_type: EventType = field(default=EventType.NOTHING, init=False)