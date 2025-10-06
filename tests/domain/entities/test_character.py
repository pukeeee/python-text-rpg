# tests/domain/entities/test_character.py
"""
Юніт-тести для сутності Character.

Ці тести перевіряють бізнес-логіку, інкапсульовану в класі Character,
в повній ізоляції від зовнішніх залежностей, таких як база даних.
"""
import pytest
from domain.entities.character import Character
from domain.value_objects.stats import BaseStats


@pytest.fixture
def base_stats() -> BaseStats:
    """Фікстура для створення базового об'єкта характеристик."""
    return BaseStats(strength=10, dexterity=10, intelligence=10, base_health=100, base_mana=50)


@pytest.fixture
def character(base_stats: BaseStats) -> Character:
    """Фікстура для створення свіжого екземпляра персонажа перед кожним тестом."""
    return Character(
        telegram_user_id=123,
        name="Test Unit",
        base_stats=base_stats
    )


class TestCharacterLogic:
    """Групує юніт-тести для бізнес-логіки класу Character."""

    def test_initial_health_and_mana(self, character: Character, base_stats: BaseStats):
        """Перевіряє, що початкове здоров'я і мана дорівнюють базовим, якщо не вказано інше."""
        assert character.current_health == base_stats.base_health
        assert character.current_mana == base_stats.base_mana

    def test_is_alive(self, character: Character):
        """Тестує логіку методу is_alive()."""
        assert character.is_alive() is True

        character.current_health = 1
        assert character.is_alive() is True

        character.current_health = 0
        assert character.is_alive() is False

        character.current_health = -10 # Хоча логіка take_damage це запобігає, перевіримо граничний випадок
        assert character.is_alive() is False

    def test_take_damage_reduces_health(self, character: Character):
        """Перевіряє, що нанесення шкоди коректно зменшує здоров'я."""
        initial_health = character.current_health
        damage = 30
        character.take_damage(damage)
        assert character.current_health == initial_health - damage

    def test_take_more_damage_than_health(self, character: Character):
        """Перевіряє, що здоров'я не може стати від'ємним."""
        character.take_damage(character.current_health + 50)
        assert character.current_health == 0
        assert character.is_alive() is False

    def test_take_zero_damage(self, character: Character):
        """Перевіряє, що нанесення нульової шкоди не змінює здоров'я."""
        initial_health = character.current_health
        character.take_damage(0)
        assert character.current_health == initial_health

    def test_take_negative_damage(self, character: Character):
        """Перевіряє, що нанесення від'ємної шкоди не змінює здоров'я."""
        initial_health = character.current_health
        character.take_damage(-20)
        assert character.current_health == initial_health
