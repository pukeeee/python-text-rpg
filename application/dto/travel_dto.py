"""
Data Transfer Objects (DTOs) для подорожей.
"""
from dataclasses import dataclass

@dataclass
class TravelRequest:
    """Запит на переміщення персонажа в іншу локацію."""
    character_id: str
    destination_id: str

@dataclass
class TravelResponse:
    """Відповідь після спроби переміщення."""
    success: bool
    new_location_name: str
    message: str
