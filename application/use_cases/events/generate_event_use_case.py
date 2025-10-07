"""
Use Case для генерації випадкової події.
"""
from dataclasses import dataclass
from domain.services.event_generator import EventGenerator
from domain.repositories.character_repository import ICharacterRepository
# Поки що локації захардкодимо, в майбутньому потрібен репозиторій локацій
from domain.entities.location import Location

@dataclass
class GenerateEventRequest:
    character_id: str

@dataclass
class GenerateEventResponse:
    event_type: str
    description: str
    data: dict

class GenerateEventUseCase:
    def __init__(self, character_repo: ICharacterRepository, event_generator: EventGenerator):
        self.character_repo = character_repo
        self.event_generator = event_generator
        # TODO: Замінити на репозиторій локацій
        self.locations = {
            "forest_dark": Location(
                id="forest_dark",
                name="Темний Ліс",
                type="wilderness",
                description="Небезпечний ліс, сповнений монстрів та скарбів.",
                available_actions=["explore", "travel"],
                event_pool=[
                    {"event_type": "combat", "probability": 0.7},
                    {"event_type": "chest", "probability": 0.2},
                    {"event_type": "nothing", "probability": 0.1}
                ],
                connected_locations=["town_main"]
            )
        }

    def execute(self, request: GenerateEventRequest) -> GenerateEventResponse:
        character = self.character_repo.get(request.character_id)
        if not character:
            raise ValueError("Персонаж не знайдений")

        location = self.locations.get(character.location_id)
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
