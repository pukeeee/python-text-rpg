"""
Use Case для переміщення персонажа між локаціями.
"""
from dataclasses import dataclass
from domain.repositories.character_repository import ICharacterRepository
from domain.repositories.location_repository import ILocationRepository
from application.dto.travel_dto import TravelRequest, TravelResponse

class TravelUseCase:
    """Керує логікою переміщення персонажа."""

    def __init__(self, character_repo: ICharacterRepository, location_repo: ILocationRepository):
        self.character_repo = character_repo
        self.location_repo = location_repo

    def execute(self, request: TravelRequest) -> TravelResponse:
        """Виконує переміщення."""
        character = self.character_repo.get(request.character_id)
        if not character:
            raise ValueError("Персонаж не знайдений")

        current_location = self.location_repo.get(character.location_id)
        if not current_location:
            raise ValueError("Поточна локація персонажа не знайдена")

        destination = self.location_repo.get(request.destination_id)
        if not destination:
            return TravelResponse(success=False, new_location_name="", message="Локація призначення не знайдена.")

        if destination.id not in current_location.connected_locations:
            return TravelResponse(
                success=False,
                new_location_name="",
                message=f"Ви не можете подорожувати з '{current_location.name}' до '{destination.name}'."
            )

        character.travel_to(destination.id)
        self.character_repo.save(character)

        return TravelResponse(
            success=True,
            new_location_name=destination.name,
            message=f"Ви прибули до локації: {destination.name}."
        )
