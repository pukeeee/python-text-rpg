"""
Відповідає за створення та управління сесіями SQLAlchemy.

Надає фабрику сесій та контекстний менеджер для забезпечення патерну Unit of Work.
"""
from contextlib import contextmanager
from typing import Iterator
from sqlalchemy.orm import sessionmaker, scoped_session, Session

# Імпортуємо вже створений рушій з сусіднього модуля.
from .engine import engine

# Створюємо потоко-безпечну фабрику сесій.
# scoped_session гарантує, що кожен потік працює з власним екземпляром сесії,
# що є критичним для веб-додатків або багатопоточних програм.
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

@contextmanager
def get_session() -> Iterator[Session]:
    """
    Контекстний менеджер, що надає сесію для виконання операцій.

    Забезпечує правильне закриття сесії та відкат транзакції в разі помилки.
    Рішення про коміт (commit) приймається ззовні, у коді бізнес-логіки.
    """
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
