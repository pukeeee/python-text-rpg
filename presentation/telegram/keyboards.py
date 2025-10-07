"""
Створення Inline-клавіатур для інтерактивної взаємодії.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
