"""
Обробники команд та повідомлень для Telegram-бота.
"""
import os
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from infrastructure.persistence.database.session import get_session
from infrastructure.persistence.repositories.postgres_character_repository import PostgresCharacterRepository
from infrastructure.persistence.repositories.json_item_repository import JsonItemRepository
from infrastructure.persistence.repositories.json_enemy_repository import JsonEnemyRepository
from infrastructure.persistence.repositories.json_location_repository import JsonLocationRepository

from domain.services.stats_calculator import StatsCalculator
from domain.services.combat_calculator import CombatCalculator
from domain.services.event_generator import EventGenerator
from domain.services.loot_generator import LootGenerator

from application.use_cases.character import CreateCharacterUseCase, GetCharacterStatsUseCase
from application.use_cases.character.travel import TravelUseCase
from application.use_cases.combat.start_combat import StartCombatUseCase
from application.use_cases.combat.perform_attack_use_case import PerformAttackUseCase
from application.use_cases.events.generate_event_use_case import GenerateEventUseCase
from application.dto.character_dto import CreateCharacterRequest, GetCharacterStatsRequest
from application.dto.travel_dto import TravelRequest

from .formatters import format_stats_response, format_attack_response
from .keyboards import get_travel_keyboard

logger = logging.getLogger(__name__)
router = Router()

# Шлях до ігрових даних
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обробник команди /start."""
    if not message.from_user:
        logger.warning("Повідомлення без користувача в cmd_start.")
        return
    user_id = message.from_user.id

    with get_session() as session:
        character_repo = PostgresCharacterRepository(session)
        existing = character_repo.get_by_telegram_user_id(user_id)

        if existing:
            await message.answer(
                f"🎮 З поверненням, {existing.name}!\n\n"
                f"📊 Рівень: {existing.level}\n"
                f"❤️ Здоров'я: {existing.current_health}/{existing.base_stats.base_health}\n\n"
                f"Використовуйте /help для списку команд."
            )
            return

        await message.answer(
            "🎮 Ласкаво просимо до текстової RPG!\n\n"
            "Введіть ім'я вашого персонажа (3-20 символів):"
        )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обробник команди /stats."""
    if not message.from_user:
        logger.warning("Повідомлення без користувача в cmd_stats.")
        return
    user_id = message.from_user.id

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            item_repo = JsonItemRepository(DATA_PATH)
            stats_calculator = StatsCalculator(item_repo)

            use_case = GetCharacterStatsUseCase(character_repo, stats_calculator)
            request = GetCharacterStatsRequest(telegram_user_id=user_id)
            response = use_case.execute(request)

            text = format_stats_response(response)
            await message.answer(text, parse_mode="HTML")

        except ValueError as e:
            await message.answer(f"❌ Помилка: {e}")


@router.message(Command("explore"))
async def cmd_explore(message: Message):
    """Обробник команди /explore."""
    if not message.from_user:
        logger.warning("Повідомлення без користувача в cmd_explore.")
        return
    user_id = message.from_user.id

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            character = character_repo.get_by_telegram_user_id(user_id)

            if not character:
                await message.answer("❌ Спочатку створіть персонажа: /start")
                return

            if character.combat_state:
                await message.answer("⚔️ Ви вже в бою! Використовуйте /attack")
                return

            event_generator = EventGenerator()
            location_repo = JsonLocationRepository(DATA_PATH)
            use_case = GenerateEventUseCase(character_repo, location_repo, event_generator)
            from application.use_cases.events.generate_event_use_case import GenerateEventRequest
            request = GenerateEventRequest(character_id=character.id)
            response = use_case.execute(request)

            if response.event_type == "combat":
                enemy_repo = JsonEnemyRepository(DATA_PATH)
                item_repo = JsonItemRepository(DATA_PATH)
                stats_calculator = StatsCalculator(item_repo)
                location_repo = JsonLocationRepository(DATA_PATH) # Потрібен для вибору ворога
                start_combat_uc = StartCombatUseCase(
                    character_repo, enemy_repo, stats_calculator, location_repo
                )
                from application.use_cases.combat.start_combat import StartCombatRequest
                combat_response = start_combat_uc.execute(
                    StartCombatRequest(character_id=character.id)
                )
                session.commit()
                await message.answer(
                    f"⚔️ <b>БІЙ!</b>\n\n"
                    f"{combat_response.message}\n\n"
                    f"🧟 Ворог: {combat_response.enemy_name}\n"
                    f"❤️ Здоров'я ворога: {combat_response.enemy_health}\n\n"
                    f"Використовуйте /attack щоб атакувати!",
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    f"🔍 {response.description}\n\n"
                    f"Продовжуйте дослідження: /explore"
                )

        except Exception as e:
            logger.error(f"Помилка в cmd_explore: {e}", exc_info=True)
            await message.answer(f"❌ Помилка: {str(e)}")


@router.message(Command("attack"))
async def cmd_attack(message: Message):
    """Обробник команди /attack."""
    if not message.from_user:
        logger.warning("Повідомлення без користувача в cmd_attack.")
        return
    user_id = message.from_user.id

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            character = character_repo.get_by_telegram_user_id(user_id)

            if not character:
                await message.answer("❌ Спочатку створіть персонажа: /start")
                return

            if not character.combat_state:
                await message.answer(
                    "❌ Ви не в бою!\n"
                    "Використовуйте /explore щоб знайти ворога."
                )
                return

            enemy_repo = JsonEnemyRepository(DATA_PATH)
            item_repo = JsonItemRepository(DATA_PATH)
            stats_calculator = StatsCalculator(item_repo)
            combat_calculator = CombatCalculator()
            loot_generator = LootGenerator()
            use_case = PerformAttackUseCase(
                character_repo,
                enemy_repo,
                stats_calculator,
                combat_calculator,
                loot_generator
            )

            from application.use_cases.combat.perform_attack_use_case import PerformAttackRequest
            request = PerformAttackRequest(character_id=character.id, number_of_attacks=1)
            response = use_case.execute(request)
            session.commit()

            text = format_attack_response(response)
            await message.answer(text, parse_mode="HTML")

        except ValueError as e:
            await message.answer(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Помилка в cmd_attack: {e}", exc_info=True)
            await message.answer(f"❌ Помилка: {str(e)}")


@router.message(Command("travel"))
async def cmd_travel(message: Message):
    """Обробник команди /travel."""
    if not message.from_user:
        logger.warning("Повідомлення без користувача в cmd_travel.")
        return
    user_id = message.from_user.id

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            character = character_repo.get_by_telegram_user_id(user_id)

            if not character:
                await message.answer("❌ Спочатку створіть персонажа: /start")
                return

            if character.combat_state:
                await message.answer("⚔️ Ви не можете подорожувати під час бою!")
                return

            location_repo = JsonLocationRepository(DATA_PATH)
            current_location = location_repo.get(character.location_id)

            if not current_location or not current_location.connected_locations:
                await message.answer("🗺 Звідси немає куди подорожувати.")
                return

            destinations = [
                loc for loc_id in current_location.connected_locations
                if (loc := location_repo.get(loc_id))
            ]

            if not destinations:
                await message.answer("🗺 Не знайдено доступних локацій для подорожі.")
                return

            keyboard = get_travel_keyboard(destinations)
            await message.answer(
                f"Ви знаходитесь в: <b>{current_location.name}</b>\n\n"
                f"Куди бажаєте відправитись?",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"Помилка в cmd_travel: {e}", exc_info=True)
            await message.answer(f"❌ Помилка: {str(e)}")


@router.callback_query(F.data.startswith("travel_to:"))
async def on_travel_callback(callback: CallbackQuery):
    """Обробник для кнопок подорожі."""
    if not callback.from_user:
        return

    user_id = callback.from_user.id
    destination_id = callback.data.split(':')[1]

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            character = character_repo.get_by_telegram_user_id(user_id)
            if not character:
                await callback.answer("Персонаж не знайдений.", show_alert=True)
                return

            location_repo = JsonLocationRepository(DATA_PATH)
            use_case = TravelUseCase(character_repo, location_repo)
            request = TravelRequest(character_id=character.id, destination_id=destination_id)
            response = use_case.execute(request)
            session.commit()

            if response.success:
                await callback.message.edit_text(
                    f"✅ {response.message}\n\n"
                    f"Тепер ви можете досліджувати нову місцевість: /explore"
                )
            else:
                await callback.message.edit_text(f"❌ {response.message}")

        except Exception as e:
            logger.error(f"Помилка в on_travel_callback: {e}", exc_info=True)
            await callback.answer(f"Помилка: {str(e)}", show_alert=True)

    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обробник команди /help."""
    text = (
        "🎮 <b>Доступні команди:</b>\n\n"
        "👤 <b>Персонаж:</b>\n"
        "/start - Почати гру / Створити персонажа\n"
        "/stats - Переглянути характеристики\n"
        "/inventory - Переглянути інвентар\n\n"

        "🗺 <b>Дослідження:</b>\n"
        "/explore - Досліджувати локацію\n"
        "/travel - Подорожувати до іншої локації\n"
        "/rest - Відпочити в місті (відновлює здоров'я)\n\n"

        "⚔️ <b>Бій:</b>\n"
        "/attack - Атакувати ворога\n"
        "/flee - Втекти з бою\n\n"

        "/help - Показати цю довідку\n"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("inventory"))
async def cmd_inventory(message: Message):
    """Обробник команди /inventory - показ інвентаря"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            character = character_repo.get_by_telegram_user_id(user_id)

            if not character:
                await message.answer("❌ Спочатку створіть персонажа: /start")
                return

            if not character.inventory:
                await message.answer("🎒 Ваш інвентар порожній")
                return

            # Завантажуємо предмети
            item_repo = JsonItemRepository(DATA_PATH)
            # items = item_repo.get_many_by_ids(character.inventory)

            # Рахуємо кількість кожного предмета
            item_counts = {}
            for item_id in character.inventory:
                item_counts[item_id] = item_counts.get(item_id, 0) + 1

            text = "🎒 <b>ВАШ ІНВЕНТАР:</b>\n\n"

            for item_id, count in item_counts.items():
                item = item_repo.get_by_id(item_id)
                if item:
                    emoji = "⚔️" if item.type == "weapon" else "🛡" if item.type == "armor" else "🧪"
                    text += f"{emoji} {item.name} x{count}\n"
                    text += f"   └ {item.description}\n"

            # Показуємо екіпіровку
            text += "\n<b>ЕКІПІРОВАНО:</b>\n"
            equipped_any = False
            for slot, item_id in character.equipped_items.items():
                if item_id:
                    item = item_repo.get_by_id(item_id)
                    if item:
                        text += f"• {slot}: {item.name}\n"
                        equipped_any = True

            if not equipped_any:
                text += "Нічого не екіпіровано\n"

            await message.answer(text, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Помилка в cmd_inventory: {e}", exc_info=True)
            await message.answer(f"❌ Помилка: {str(e)}")


@router.message(Command("rest"))
async def cmd_rest(message: Message):
    """Обробник команди /rest - відпочинок в місті"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            character = character_repo.get_by_telegram_user_id(user_id)

            if not character:
                await message.answer("❌ Спочатку створіть персонажа: /start")
                return

            # Перевіряємо чи персонаж в місті
            location_repo = JsonLocationRepository(DATA_PATH)
            location = location_repo.get(character.location_id)

            if not location or location.type != "town":
                await message.answer(
                    "❌ Відпочивати можна тільки в місті!\n"
                    "Поверніться до міста за допомогою /travel"
                )
                return

            # Перевіряємо чи персонаж в бою
            if character.combat_state:
                await message.answer("⚔️ Ви не можете відпочивати під час бою!")
                return

            # Розраховуємо максимальні значення
            item_repo = JsonItemRepository(DATA_PATH)
            stats_calculator = StatsCalculator(item_repo)
            stats = stats_calculator.calculate_total_stats(character)

            # Відновлюємо здоров'я та ману
            health_restored = stats.max_health - character.current_health
            mana_restored = stats.max_mana - character.current_mana

            character.current_health = stats.max_health
            character.current_mana = stats.max_mana

            character_repo.save(character)
            session.commit()

            await message.answer(
                f"😴 <b>Ви відпочили в таверні!</b>\n\n"
                f"❤️ Здоров'я відновлено: +{health_restored}\n"
                f"💙 Мана відновлена: +{mana_restored}\n\n"
                f"Ви готові до нових пригод! /explore",
                parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"Помилка в cmd_rest: {e}", exc_info=True)
            await message.answer(f"❌ Помилка: {str(e)}")


@router.message(Command("flee"))
async def cmd_flee(message: Message):
    """Обробник команди /flee - втеча з бою"""
    if not message.from_user:
        return
    user_id = message.from_user.id

    with get_session() as session:
        try:
            character_repo = PostgresCharacterRepository(session)
            character = character_repo.get_by_telegram_user_id(user_id)

            if not character:
                await message.answer("❌ Спочатку створіть персонажа: /start")
                return

            if not character.combat_state:
                await message.answer("❌ Ви не в бою!")
                return

            # Шанс на втечу залежить від спритності
            import random
            flee_chance = min(0.5 + (character.base_stats.dexterity * 0.02), 0.9)

            if random.random() < flee_chance:
                # Успішна втеча
                character.combat_state = None
                character_repo.save(character)
                session.commit()

                await message.answer(
                    "🏃 <b>Ви успішно втекли з бою!</b>\n\n"
                    "Можливо варто повернутись в місто та відпочити? /travel",
                    parse_mode="HTML"
                )
            else:
                # Невдала втеча - ворог атакує
                enemy_repo = JsonEnemyRepository(DATA_PATH)
                enemy = enemy_repo.get_by_id(character.combat_state['enemy_id'])

                if enemy:
                    enemy.current_health = character.combat_state['enemy_current_health']

                    item_repo = JsonItemRepository(DATA_PATH)
                    stats_calculator = StatsCalculator(item_repo)
                    combat_calculator = CombatCalculator()

                    player_stats = stats_calculator.calculate_total_stats(character)
                    enemy_stats = enemy.stats

                    # Ворог атакує один раз
                    is_hit, is_crit, damage = combat_calculator.perform_single_attack(
                        enemy_stats, player_stats
                    )

                    if is_hit:
                        character.take_damage(damage)
                        character_repo.save(character)
                        session.commit()

                        crit_text = "💥 КРИТИЧНИЙ УДАР! " if is_crit else ""
                        await message.answer(
                            f"❌ <b>Втеча не вдалась!</b>\n\n"
                            f"Ворог встиг вас вдарити:\n"
                            f"{crit_text}Урон: {damage}\n\n"
                            f"❤️ Ваше здоров'я: {character.current_health}\n\n"
                            f"Продовжуйте битись: /attack",
                            parse_mode="HTML"
                        )
                    else:
                        await message.answer(
                            "❌ Втеча не вдалась, але ворог промахнувся!\n\n"
                            "Спробуйте ще раз: /flee або атакуйте: /attack"
                        )

        except Exception as e:
            logger.error(f"Помилка в cmd_flee: {e}", exc_info=True)
            await message.answer(f"❌ Помилка: {str(e)}")


@router.message()
async def handle_text(message: Message):
    """Обробка текстових повідомлень для створення персонажа."""
    if not message.from_user:
        logger.warning("Повідомлення без користувача в handle_text.")
        return

    if not message.text:
        await message.answer("Будь ласка, введіть ім'я для вашого персонажа.")
        return

    user_id = message.from_user.id
    character_name = message.text.strip()

    with get_session() as session:
        character_repo = PostgresCharacterRepository(session)
        existing = character_repo.get_by_telegram_user_id(user_id)

        if existing:
            await message.answer(
                "Ви вже маєте персонажа! Використовуйте /help для списку команд."
            )
            return

        try:
            use_case = CreateCharacterUseCase(character_repo)
            request = CreateCharacterRequest(
                telegram_user_id=user_id,
                character_name=character_name
            )
            response = use_case.execute(request)
            session.commit()

            await message.answer(
                f"✅ {response.message}\n\n"
                f"👤 Ім'я: {response.character_name}\n"
                f"⭐️ Рівень: {response.level}\n\n"
                f"Використовуйте /help щоб подивитись доступні команди.\n"
                f"Почніть своє пригоду з /explore!"
            )
        except ValueError as e:
            await message.answer(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Помилка створення персонажа: {e}", exc_info=True)
            await message.answer(f"❌ Помилка: {str(e)}")
