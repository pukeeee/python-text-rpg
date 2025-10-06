"""
Відповідає за створення та конфігурацію рушія (engine) SQLAlchemy.

Engine - це центральний об'єкт, що керує пулом з'єднань з базою даних.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def create_db_engine() -> Engine:
    """
    Створює та повертає екземпляр рушія SQLAlchemy на основі змінних оточення.
    """
    database_url = os.getenv(
        'DATABASE_URL',
        'postgresql://rpg_user:password@localhost:5432/rpg_game'
    )

    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
    )
    return engine

# Створюємо глобальний екземпляр рушія для використання в усьому додатку.
engine = create_db_engine()

def create_tables(engine_instance: Engine = engine) -> None:
    """
    Створює всі таблиці. Дозволяє передати інший рушій для тестування.
    """
    from .models import Base
    Base.metadata.create_all(engine_instance)

def drop_tables(engine_instance: Engine = engine) -> None:
    """
    Видаляє всі таблиці. Дозволяє передати інший рушій для тестування.
    """
    from .models import Base
    Base.metadata.drop_all(engine_instance)
