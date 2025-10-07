"""
Модуль для форматування текстових відповідей для Telegram-бота.
"""
from application.use_cases.character.get_character_stats import GetCharacterStatsResponse
from application.use_cases.combat.perform_attack_use_case import PerformAttackResponse


def format_stats_response(response: GetCharacterStatsResponse) -> str:
    """Форматує відповідь зі статистикою персонажа."""
    stats = response.stats
    return (
        f"👤 <b>{response.name}</b> (Рівень {response.level})\n"
        f"📍 Локація: {response.location}\n"
        f"⭐️ Досвід: {response.experience}/{response.experience_to_next_level}\n\n"

        f"<b>📊 Базові характеристики:</b>\n"
        f"💪 Сила: {stats.strength}\n"
        f"🎯 Спритність: {stats.dexterity}\n"
        f"🧠 Інтелект: {stats.intelligence}\n\n"

        f"<b>❤️ Життя та енергія:</b>\n"
        f"❤️ Здоров'я: {stats.health}/{stats.max_health}\n"
        f"💙 Мана: {stats.mana}/{stats.max_mana}\n\n"

        f"<b>🛡 Захист:</b>\n"
        f"🛡 Броня: {stats.armor}\n"
        f"💨 Ухилення: {stats.evasion}\n"
        f"⚡️ Енергетичний щит: {stats.energy_shield}\n\n"

        f"<b>⚔️ Атака:</b>\n"
        f"⚔️ Урон: {stats.damage_min}-{stats.damage_max}\n"
        f"🎯 Точність: {stats.accuracy}\n"
        f"💥 Шанс криту: {stats.critical_chance:.1f}%\n"
        f"💢 Множник криту: x{stats.critical_multiplier:.1f}\n"
        f"⚡️ Швидкість атаки: {stats.attack_speed:.2f}\n"
    )


def format_attack_response(response: PerformAttackResponse) -> str:
    """Форматує текстову відповідь для результатів раунду бою."""
    text = "⚔️ <b>РАУНД БОЮ</b>\n\n"

    # Атаки гравця
    for attack in response.player_attacks:
        if attack.is_hit:
            crit = "💥 КРИТИЧНИЙ! " if attack.is_critical else ""
            text += f"⚔️ Ви завдали {crit}{attack.damage} урону!\n"
        else:
            text += "❌ Ви промахнулись!\n"

    # Атаки ворога
    for attack in response.enemy_attacks:
        if attack.is_hit:
            crit = "💥 КРИТИЧНИЙ! " if attack.is_critical else ""
            text += f"🧟 Ворог завдав вам {crit}{attack.damage} урону!\n"
        else:
            text += "✅ Ворог промахнувся!\n"

    text += f"\n{response.message}\n"

    if response.combat_ended:
        if response.victor == "player":
            text += "\n🎉 <b>ПЕРЕМОГА!</b>\n\n"
            if response.rewards:
                text += f"⭐️ Досвід: +{response.rewards.experience_gained}\n"
                text += f"💰 Золото: +{response.rewards.gold_gained}\n"
                if response.rewards.items_gained:
                    text += f"🎁 Предмети: {len(response.rewards.items_gained)} шт.\n"
                if response.rewards.level_up:
                    text += "\n🆙 <b>НОВИЙ РІВЕНЬ!</b>\n"
        else:
            text += "\n💀 <b>ПОРАЗКА...</b>\n"

        text += "\nВикористовуйте /explore щоб продовжити пригоди!"
    else:
        # Показуємо здоров'я
        if response.enemy_attacks:
            text += f"\n❤️ Ваше здоров'я: {response.enemy_attacks[0].defender_health_remaining}\n"
        if response.player_attacks:
            text += f"🧟 Здоров'я ворога: {response.player_attacks[0].defender_health_remaining}\n"

        text += "\nПродовжуйте битись: /attack"

    return text