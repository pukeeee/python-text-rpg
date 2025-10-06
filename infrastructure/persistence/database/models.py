"""
Цей модуль визначає всі моделі даних SQLAlchemy, які відповідають таблицям у базі даних.
Кожна модель представляє одну таблицю і її стовпці, а також зв'язки між таблицями.
Ці моделі використовуються репозиторіями для взаємодії з БД.
"""
from sqlalchemy import (
    String, Integer, BigInteger, DateTime,
    Numeric, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from datetime import datetime, timezone
import uuid
from decimal import Decimal

# Створення базового класу для всіх моделей за допомогою сучасного синтаксису.
# Всі наші моделі будуть наслідувати цей клас.
class Base(DeclarativeBase):
    pass

class CharacterModel(Base):
    """Модель персонажа, що зберігає основну інформацію та стан гравця."""
    __tablename__ = 'characters'

    # --- Ідентифікатори ---
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)

    # --- Основна інформація ---
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    experience: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    # --- Базові характеристики (статичні) ---
    strength: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    dexterity: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    intelligence: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    base_health: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    base_mana: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    # --- Поточний стан (динамічний) ---
    current_health: Mapped[int] = mapped_column(Integer, nullable=False)
    current_mana: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- Місцезнаходження ---
    location_id: Mapped[str] = mapped_column(String(50), nullable=False, default='town_main')

    # --- Часові мітки ---
    # default=lambda... - генерує значення за замовчуванням на стороні Python під час створення запису.
    # onupdate=lambda... - оновлює значення на стороні Python під час оновлення запису.
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # --- Зв'язки (Relationships) ---
    # `relationship` створює зв'язок з іншими моделями.
    # `back_populates` вказує на відповідне поле в зв'язаній моделі для двостороннього зв'язку.
    # `cascade="all, delete-orphan"` означає, що при видаленні персонажа, всі пов'язані з ним
    # записи (інвентар, екіпіровка і т.д.) будуть автоматично видалені.
    inventory: Mapped[list["InventoryModel"]] = relationship(back_populates="character", cascade="all, delete-orphan")
    equipment: Mapped["EquipmentModel"] = relationship(back_populates="character", uselist=False, cascade="all, delete-orphan")
    combat_state: Mapped["CombatStateModel"] = relationship(back_populates="character", uselist=False, cascade="all, delete-orphan")
    stats_cache: Mapped["StatsCacheModel"] = relationship(back_populates="character", uselist=False, cascade="all, delete-orphan")

class InventoryModel(Base):
    """Модель інвентаря персонажа. Зберігає предмети та їх кількість."""
    __tablename__ = 'character_inventory'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Зовнішній ключ, що посилається на таблицю персонажів.
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    acquired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Зворотний зв'язок до моделі CharacterModel.
    character: Mapped["CharacterModel"] = relationship(back_populates="inventory")

    # Додаткові параметри таблиці.
    __table_args__ = (
        # Унікальне обмеження: один і той же предмет не може двічі з'явитись у інвентарі одного персонажа (треба оновлювати quantity).
        UniqueConstraint('character_id', 'item_id', name='uq_character_item'),
        # Індекс для швидкого пошуку предметів за ID персонажа.
        Index('idx_character_inventory', 'character_id'),
    )

class EquipmentModel(Base):
    """Модель екіпіровки персонажа. Зберігає предмети, вдягнені на персонажа."""
    __tablename__ = 'character_equipment'

    # ID персонажа є одночасно і первинним, і зовнішнім ключем (зв'язок один-до-одного).
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), primary_key=True)

    # Слоти екіпіровки. Можуть бути порожніми (nullable=True).
    weapon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    armor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    helmet: Mapped[str | None] = mapped_column(String(100), nullable=True)
    boots: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gloves: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ring_1: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ring_2: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amulet: Mapped[str | None] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    character: Mapped["CharacterModel"] = relationship(back_populates="equipment")

class CombatStateModel(Base):
    """Модель стану бою. Створюється, коли персонаж вступає в бій."""
    __tablename__ = 'combat_states'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Унікальний зв'язок з персонажем: один персонаж може бути лише в одному бою одночасно.
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), unique=True, nullable=False)
    enemy_id: Mapped[str] = mapped_column(String(100), nullable=False)
    enemy_level: Mapped[int] = mapped_column(Integer, nullable=False)
    enemy_current_health: Mapped[int] = mapped_column(Integer, nullable=False)
    enemy_max_health: Mapped[int] = mapped_column(Integer, nullable=False)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    character: Mapped["CharacterModel"] = relationship(back_populates="combat_state")

class StatsCacheModel(Base):
    """Модель для кешування розрахованих характеристик персонажа."""
    __tablename__ = 'character_stats_cache'

    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('characters.id', ondelete='CASCADE'), primary_key=True)

    # --- Кешовані характеристики ---
    # Ці поля дублюють розрахункові дані для швидкого доступу, щоб не перераховувати їх при кожному запиті.
    total_health: Mapped[int] = mapped_column(Integer, nullable=False)
    total_mana: Mapped[int] = mapped_column(Integer, nullable=False)
    armor: Mapped[int] = mapped_column(Integer, nullable=False)
    evasion: Mapped[int] = mapped_column(Integer, nullable=False)
    energy_shield: Mapped[int] = mapped_column(Integer, nullable=False)
    damage_min: Mapped[int] = mapped_column(Integer, nullable=False)
    damage_max: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[int] = mapped_column(Integer, nullable=False)
    # Використовуємо Numeric/Decimal для точних розрахунків, де float може давати похибку.
    critical_chance: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    critical_multiplier: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    attack_speed: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    # --- Метадані кешу ---
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # Хеш, розрахований на основі екіпіровки. Якщо хеш не збігається, кеш вважається недійсним.
    equipment_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    character: Mapped["CharacterModel"] = relationship(back_populates="stats_cache")
