"""
Use Case для генерації випадкової події.
"""
from dataclasses import dataclass
from domain.services.event_generator import EventGenerator
from domain.repositories.character_repository import ICharacterRepository
from domain.repositories.location_repository import ILocationRepository

@dataclass
class GenerateEventRequest:
    character_id: str

@dataclass
class GenerateEventResponse:
    event_type: str
    description: str
    data: dict

class GenerateEventUseCase:
    def __init__(self, character_repo: ICharacterRepository, location_repo: ILocationRepository, event_generator: EventGenerator):
        self.character_repo = character_repo
        self.location_repo = location_repo
        self.event_generator = event_generator

    def execute(self, request: GenerateEventRequest) -> GenerateEventResponse:
        character = self.character_repo.get(request.character_id)
        if not character:
            raise ValueError("Персонаж не знайдений")

        location = self.location_repo.get(character.location_id)
        if not location:
            raise ValueError("Локація не знайдена")

        event = self.event_generator.generate(location)

        # Тут може бути логіка для збереження стану події, якщо потрібно
        # наприклад, для бою

        return GenerateEventResponse(
            event_type=event.event_type.value,
            description=event.description,
            data=event.__dict__
        )
