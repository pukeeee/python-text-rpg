# tests/conftest.py
"""
Цей файл містить загальні фікстури для всіх тестів.
`pytest` автоматично знаходить і використовує цей файл.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from infrastructure.persistence.database import Base


@pytest.fixture(scope="session")
def db_engine():
    """Створює рушій БД лише один раз за тестову сесію."""
    # Якщо змінна DATABASE_URL не встановлена, спробуємо завантажити її з .env.test
    # Це робить тести стійкими до проблем з порядком завантаження у pytest
    if not os.getenv("DATABASE_URL"):
        load_dotenv(".env.test")

    test_db_url = os.getenv("DATABASE_URL")
    if not test_db_url:
        pytest.fail(
            "DATABASE_URL для тестів не встановлено. "
            "Перевірте, що файл .env.test існує в корені проекту та містить цю змінну."
        )

    engine = create_engine(test_db_url)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Створює сесію БД для кожного тесту та відкатує всі зміни після завершення.
    Це гарантує, що кожен тест працює з чистою БД.
    """
    connection = db_engine.connect()
    # Починаємо транзакцію
    transaction = connection.begin()
    # Створюємо сесію, прив'язану до цієї транзакції
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    # Створюємо всі таблиці перед тестом
    Base.metadata.create_all(bind=connection)

    # Передаємо сесію в тест
    yield session

    # Після завершення тесту закриваємо сесію і відкатуємо транзакцію
    session.close()
    transaction.rollback()
    connection.close()
