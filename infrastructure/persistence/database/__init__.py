"""
Пакет для взаємодії з базою даних.

Надає доступ до базових компонентів SQLAlchemy: Base для моделей,
engine для з'єднання та get_session для управління транзакціями.
"""
from .models import Base
from .engine import engine, create_tables, drop_tables
from .session import SessionLocal, get_session

__all__ = [
    "Base",
    "engine",
    "create_tables",
    "drop_tables",
    "SessionLocal",
    "get_session",
]
