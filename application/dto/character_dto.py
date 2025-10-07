from dataclasses import dataclass


@dataclass
class CreateCharacterRequest:
    """Запит на створення персонажа"""
    telegram_user_id: int
    character_name: str

@dataclass
class CreateCharacterResponse:
    """Відповідь зі створеним персонажем"""
    character_id: str
    character_name: str
    level: int
    message: str

@dataclass
class GetCharacterStatsRequest:
    """Запит на отримання характеристик персонажа"""
    telegram_user_id: int

@dataclass
class StatsDTO:
    """DTO для відображення характеристик"""
    # Базові
    strength: int
    dexterity: int
    intelligence: int

    # Здоров'я та мана
    health: int
    max_health: int
    mana: int
    max_mana: int

    # Захист
    armor: int
    evasion: int
    energy_shield: int

    # Атака
    damage_min: int
    damage_max: int
    accuracy: int
    critical_chance: float
    critical_multiplier: float
    attack_speed: float

@dataclass
class GetCharacterStatsResponse:
    """Відповідь з характеристиками персонажа"""
    character_id: str
    name: str
    level: int
    experience: int
    experience_to_next_level: int
    stats: StatsDTO
    location: str
