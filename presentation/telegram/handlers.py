import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from infrastructure.persistence.database import get_session
from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository
from domain.services.stats_calculator import StatsCalculator
from application.use_cases.character import CreateCharacterUseCase, GetCharacterStatsUseCase
from application.dto.character_dto import CreateCharacterRequest, GetCharacterStatsRequest
from infrastructure.persistence.repositories.json_item_repository import JsonItemRepository

# Налаштування логування
logger = logging.getLogger(__name__)

# Створюємо роутер для обробників
router = Router()

# Зберігаємо стан створення персонажа
user_states = {}

from application.use_cases.events.generate_event_use_case import GenerateEventUseCase, GenerateEventRequest
from application.use_cases.combat.start_combat import StartCombatUseCase, StartCombatRequest
from application.use_cases.combat.perform_attack_use_case import PerformAttackUseCase, PerformAttackRequest
from domain.services.event_generator import EventGenerator
from infrastructure.persistence.repositories.json_enemy_repository import JsonEnemyRepository
from domain.services.combat_calculator import CombatCalculator
from domain.services.loot_generator import LootGenerator

# ... (існуючі імпорти)

# Зберігаємо стан не тільки для імені, але і для бою
user_states = {}

from aiogram.types import CallbackQuery
from presentation.telegram.keyboards import get_combat_keyboard

# ... (існуючі імпорти)

# === Ігрові команди ===

@router.message(Command("explore"))
async def cmd_explore(message: Message):
    """Команда /explore - дослідити локацію"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    try:
        with get_session() as session:
            char_repo = PostgresCharacterRepository(session)
            # Перевірка, чи персонаж не в бою
            character = char_repo.get_by_telegram_user_id(user_id)
            if character and character.combat_state:
                await message.answer("Ви вже в бою! Використовуйте клавіатуру нижче.", reply_markup=get_combat_keyboard())
                return

            event_generator = EventGenerator()
            use_case = GenerateEventUseCase(char_repo, event_generator)
            # ID персонажа в нашій системі - це telegram_user_id
            request = GenerateEventRequest(character_id=str(user_id))
            response = use_case.execute(request)

            await message.answer(f"Подія: {response.description}")

            if response.event_type == 'combat':
                user_states[user_id] = 'in_combat'
                item_repo = JsonItemRepository(data_path="data")
                enemy_repo = JsonEnemyRepository(data_path="data")
                stats_calculator = StatsCalculator(item_repo)
                start_combat_uc = StartCombatUseCase(char_repo, enemy_repo, stats_calculator)
                
                start_req = StartCombatRequest(character_id=str(user_id))
                start_res = start_combat_uc.execute(start_req)
                session.commit()
                await message.answer(start_res.message, reply_markup=get_combat_keyboard())

    except ValueError as e:
        await message.answer(f"❌ Помилка: {e}")
    except Exception as e:
        logger.error(f"Помилка в /explore для user_id={user_id}: {e}", exc_info=True)
        await message.answer("❌ Сталася непередбачена помилка.")

@router.callback_query(lambda c: c.data and c.data.startswith('attack:'))
async def process_attack_callback(callback_query: CallbackQuery):
    """Обробка натискання кнопок атаки."""
    user_id = callback_query.from_user.id
    if user_states.get(user_id) != 'in_combat':
        await callback_query.answer("Ви не в бою.", show_alert=True)
        return

    try:
        num_attacks = int(callback_query.data.split(':')[1])
    except (ValueError, IndexError):
        await callback_query.answer("Некоректний формат атаки.")
        return

    try:
        with get_session() as session:
            char_repo = PostgresCharacterRepository(session)
            item_repo = JsonItemRepository(data_path="data")
            enemy_repo = JsonEnemyRepository(data_path="data")
            stats_calculator = StatsCalculator(item_repo)
            combat_calculator = CombatCalculator()
            loot_generator = LootGenerator()

            use_case = PerformAttackUseCase(
                char_repo, enemy_repo, stats_calculator, combat_calculator, loot_generator
            )
            request = PerformAttackRequest(character_id=str(user_id), number_of_attacks=num_attacks)
            response = use_case.execute(request)
            session.commit()

            result_message = ""
            for attack in response.player_attacks:
                result_message += f"Ви атакували: {'Попадання' if attack.is_hit else 'Промах'}, шкода: {attack.damage}\n"
            for attack in response.enemy_attacks:
                result_message += f"Ворог атакував: {'Попадання' if attack.is_hit else 'Промах'}, шкода: {attack.damage}\n"
            
            result_message += f"\n{response.message}"

            if response.combat_ended:
                user_states.pop(user_id, None)
                if response.rewards:
                    result_message += f"\nДосвід: +{response.rewards.experience_gained}, Золото: +{response.rewards.gold_gained}"
                # Видаляємо клавіатуру після бою
                await callback_query.message.edit_reply_markup(reply_markup=None)
            
            await callback_query.answer() # Закриваємо "годинник" на кнопці
            await callback_query.message.answer(result_message, reply_markup=get_combat_keyboard() if not response.combat_ended else None)

    except ValueError as e:
        await callback_query.answer(f"Помилка: {e}", show_alert=True)
        user_states.pop(user_id, None)
    except Exception as e:
        logger.error(f"Помилка в callback_attack для user_id={user_id}: {e}", exc_info=True)
        await callback_query.answer("Сталася непередбачена помилка.", show_alert=True)
        user_states.pop(user_id, None)
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start - початок гри"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    try:
        with get_session() as session:
            repo = PostgresCharacterRepository(session)
            existing = repo.get_by_telegram_user_id(user_id)

            if existing:
                await message.answer(
                    f"🎮 Вітаю, {existing.name}!\n\n"
                    f"Ваш персонаж вже створений.\n"
                    f"Використовуйте /stats щоб побачити характеристики."
                )
                return
    except Exception as e:
        logger.error(f"Помилка перевірки існуючого персонажа: {e}")
        # Продовжуємо, щоб користувач міг створити персонажа, якщо БД недоступна на старті
        pass


    # Якщо персонажа немає - просимо ввести ім'я
    user_states[user_id] = "awaiting_name"
    await message.answer(
        "🎮 Вітаємо в RPG!\n\n"
        "Введіть ім'я вашого персонажа (3-20 символів):"
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Команда /stats - показати характеристики"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    try:
        with get_session() as session:
            char_repo = PostgresCharacterRepository(session)
            item_repo = JsonItemRepository(data_path="data")
            calculator = StatsCalculator(item_repo)

            use_case = GetCharacterStatsUseCase(char_repo, calculator)
            request = GetCharacterStatsRequest(telegram_user_id=user_id)
            response = use_case.execute(request)

            stats = response.stats

            stats_text = (
                f"👤 **{response.name}** (Рівень {response.level})\n"
                f"📊 Досвід: {response.experience}/{response.experience_to_next_level}\n\n"

                f"❤️ Здоров'я: {stats.health}/{stats.max_health}\n"
                f"💙 Мана: {stats.mana}/{stats.max_mana}\n\n"

                f"⚔️ **Атака:**\n"
                f"• Урон: {stats.damage_min}-{stats.damage_max}\n"
                f"• Точність: {stats.accuracy}\n"
                f"• Крит. шанс: {stats.critical_chance:.1f}%\n"
                f"• Крит. множник: {stats.critical_multiplier:.1f}x\n"
                f"• Швидкість атаки: {stats.attack_speed:.2f}\n\n"

                f"🛡️ **Захист:**\n"
                f"• Броня: {stats.armor}\n"
                f"• Ухилення: {stats.evasion}\n"
                f"• Енерг. щит: {stats.energy_shield}\n\n"

                f"📈 **Характеристики:**\n"
                f"• Сила: {stats.strength}\n"
                f"• Спритність: {stats.dexterity}\n"
                f"• Інтелект: {stats.intelligence}\n\n"

                f"📍 Локація: {response.location}"
            )

            await message.answer(stats_text, parse_mode="Markdown")

    except ValueError as e:
        logger.warning(f"Помилка отримання статистики для user_id={user_id}: {e}")
        await message.answer(
            "❌ Персонаж не знайдений!\n"
            "Використовуйте /start щоб створити персонажа."
        )
    except Exception as e:
        logger.error(f"Неочікувана помилка в cmd_stats для user_id={user_id}: {e}")
        await message.answer("❌ Сталася внутрішня помилка. Спробуйте пізніше.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help - допомога"""
    help_text = (
        "🎮 **Доступні команди:**\n\n"
        "/start - Почати гру / Створити персонажа\n"
        "/stats - Показати характеристики персонажа\n"
        "/help - Показати це повідомлення\n\n"
        "🚧 В розробці:\n"
        "• /explore - Дослідження локацій\n"
        "• /attack - Атака в бою\n"
        "• /inventory - Інвентар та екіпіровка"
    )

    await message.answer(help_text, parse_mode="Markdown")

# === Обробка створення персонажа ===

@router.message()
async def handle_message(message: Message):
    """Обробка всіх інших повідомлень"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    # Якщо користувач у стані введення імені
    if user_states.get(user_id) == "awaiting_name":
        if not message.text:
            await message.answer("Будь ласка, введіть ім'я текстом.")
            return
        character_name = message.text.strip()

        try:
            with get_session() as session:
                repo = PostgresCharacterRepository(session)
                use_case = CreateCharacterUseCase(repo)

                request = CreateCharacterRequest(
                    telegram_user_id=user_id,
                    character_name=character_name
                )

                response = use_case.execute(request)
                session.commit()

                # Очищуємо стан
                user_states.pop(user_id, None)

                await message.answer(
                    f"✅ {response.message}\n\n"
                    f"🎉 Рівень: {response.level}\n"
                    f"📊 Використовуйте /stats щоб побачити характеристики"
                )

        except ValueError as e:
            await message.answer(f"❌ Помилка: {str(e)}")
        except Exception as e:
            logger.error(f"Неочікувана помилка при створенні персонажа для user_id={user_id}: {e}")
            await message.answer("❌ Сталася внутрішня помилка. Спробуйте пізніше.")
    else:
        await message.answer(
            "Невідома команда. Використовуйте /start щоб почати гру або /help для допомоги."
        )