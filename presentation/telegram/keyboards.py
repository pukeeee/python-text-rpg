"""
Створення Inline-клавіатур для інтерактивної взаємодії.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from domain.entities.location import Location

def get_combat_keyboard() -> InlineKeyboardMarkup:
    """Повертає клавіатуру для бойових дій."""
    buttons = [
        [
            InlineKeyboardButton(text="⚔️ Атака x1", callback_data="attack:1"),
            InlineKeyboardButton(text="⚔️ Атака x2", callback_data="attack:2"),
            InlineKeyboardButton(text="⚔️ Атака x3", callback_data="attack:3"),
        ],
        [
            InlineKeyboardButton(text="🏃 Втекти", callback_data="flee"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_travel_keyboard(destinations: List[Location]) -> InlineKeyboardMarkup:
    """Створює клавіатуру для вибору локації для подорожі."""
    buttons = []
    for dest in destinations:
        button = InlineKeyboardButton(
            text=f"📍 {dest.name}",
            callback_data=f"travel_to:{dest.id}"
        )
        buttons.append([button])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
