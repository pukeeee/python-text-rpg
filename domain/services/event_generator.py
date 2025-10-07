"""
Сервіс для генерації випадкових ігрових подій.
"""
import random

from domain.entities.event import BaseEvent, CombatEvent, ChestEvent, TownRestEvent, NothingEvent, EventType
from domain.entities.location import Location

class EventGenerator:
    """Генерує події на основі пулу подій поточної локації."""

    def generate(self, location: Location) -> BaseEvent:
        """
        Вибирає та створює випадкову подію.
        """
        event_pool = location.event_pool
        if not event_pool:
            return NothingEvent(description="Тиша та спокій...")

        event_type_str = random.choices(
            [event['event_type'] for event in event_pool],
            [event['probability'] for event in event_pool],
            k=1
        )[0]

        event_type = EventType(event_type_str)

        if event_type == EventType.COMBAT:
            return CombatEvent(description="На вас напали!", enemy_id="generic_enemy")
        elif event_type == EventType.CHEST:
            return ChestEvent(description="Ви знайшли скарб!", loot={})
        elif event_type == EventType.TOWN_REST:
            return TownRestEvent(description="Ви в безпечному місті.")
        else:
            return NothingEvent(description="Нічого цікавого не сталося.")