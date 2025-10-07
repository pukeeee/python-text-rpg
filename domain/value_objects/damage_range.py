from dataclasses import dataclass

@dataclass(frozen=True)
class DamageRange:
    """Диапазон урона"""
    min_damage: int
    max_damage: int

    def __post_init__(self):
        if self.min_damage < 0 or self.max_damage < 0:
            raise ValueError("Damage cannot be negative")
        if self.min_damage > self.max_damage:
            raise ValueError("Min damage cannot exceed max damage")
