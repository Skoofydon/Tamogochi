import asyncio
import logging
import sys
from os import getenv
from pathlib import Path

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_URL

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ========== Клавиатуры ==========

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    builder = InlineKeyboardBuilder()
    
    # Кнопка запуска Mini App
    builder.button(
        text="🎮 ИГРАТЬ В ТАМАГОЧИ", 
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    
    builder.adjust(1)
    
    # Второй ряд с доп кнопками
    builder.row(
        InlineKeyboardButton(text="👥 Моя общага", callback_data="dorm"),
        InlineKeyboardButton(text="🏆 Рейтинг", callback_data="rating")
    )
    builder.row(
        InlineKeyboardButton(text="🛒 Магазин", callback_data="shop"),
        InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
    )
    
    return builder.as_markup()

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Назад"""
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data="back_to_main")
    return builder.as_markup()

# ========== Обработчики команд ==========

@router.message(CommandStart())
async def command_start(message: types.Message):
    """Приветственное сообщение при старте"""
    
    # Получаем данные пользователя
    user = message.from_user
    user_name = user.first_name or "Студент"
    
    # Приветственный текст
    welcome_text = f"""
🎓 <b>Привет, {user_name}!</b>

Добро пожаловать в <b>Тамагочи-Общагу</b> — место, где ты можешь:
• 🛏️ Жить своей студенческой жизнью
• 📚 Учиться и прокачивать скиллы
• 🪙 Зарабатывать монеты
• 🥷 Воровать еду у соседей
• 🎉 Ходить на вписки

<b>Твой персонаж полностью зависит от тебя!</b>
Следи за энергией, едой и настроением.

👇 Жми кнопку ниже, чтобы начать игру!
"""
    
    # Отправляем приветствие с клавиатурой
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

# ========== Обработчики callback ==========

@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🎮 <b>Главное меню</b>\n\nВыбери действие:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "dorm")
async def show_dorm_info(callback: types.CallbackQuery):
    """Информация об общаге"""
    text = """
🏢 <b>ТВОЯ ОБЩАГА</b>

Соседи онлайн: <b>247 студентов</b>

Твои соседи по блоку:
• 🧑‍🎓 Макс (2 курс) — любит тусить
• 👩‍🎓 Аня (3 курс) — всегда учится
• 🧔‍♂️ Санёк (4 курс) — спит целыми днями

Совет: Можно стырить еду из общего холодильника, но есть шанс спалиться!

<i>Скоро здесь будет чат с соседями и PvP-режим</i>
"""
    await callback.message.edit_text(
        text, 
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "rating")
async def show_rating(callback: types.CallbackQuery):
    """Таблица лидеров"""
    text = """
🏆 <b>РЕЙТИНГ СТУДЕНТОВ</b>

Топ-5 общежития:

1. 🥇 Анна К. — 3 курс, 12,450 🪙
2. 🥈 Дима В. — 4 курс, 9,870 🪙
3. 🥉 Олег М. — 2 курс, 8,230 🪙
4. 📊 Катя С. — 3 курс, 7,150 🪙
5. 📊 Игорь П. — 1 курс, 5,980 🪙

━━━━━━━━━━━━━━━
📌 Твоя позиция: <b>42 место</b>

Зарабатывай монеты, учись и поднимайся в топ!
"""
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "shop")
async def show_shop(callback: types.CallbackQuery):
    """Магазин улучшений"""
    text = """
🛒 <b>МАГАЗИН ОБЩАГИ</b>

Доступные товары:

🍕 <b>Доставка пиццы</b> — 50 🪙
   +50 сытости, +20 настроения

☕ <b>Энергетик</b> — 30 🪙
   +40 энергии

📚 <b>Шпаргалки</b> — 40 🪙
   +25 к учёбе без затрат энергии

🎮 <b>Приставка в комнату</b> — 200 🪙
   +10 к настроению каждый час

🛏️ <b>Ортопедический матрас</b> — 150 🪙
   Сон восстанавливает на 30% больше

<i>Покупки скоро будут доступны прямо из Mini App!</i>
"""
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "help")
async def show_help(callback: types.CallbackQuery):
    """Помощь по игре"""
    text = """
ℹ️ <b>КАК ИГРАТЬ</b>

<b>🎮 Основные действия:</b>
• 🍽️ Поесть — 5🪙, +30 сытости
• 😴 Поспать — восстанавливает энергию
• 📝 Учёба — +15 к учёбе, -10 еды/энергии
• 💼 Подработка — +20-35🪙, -20 энергии
• 🥷 Стырить еду — шанс 40%, риск -20 настроения
• 🎉 Вписка — +40 настроения, -30🪙

<b>⚡ Важно:</b>
• Все показатели падают со временем
• Если показатель падает до 0 — штраф!
• За учёбу и вписки получаешь XP
• Каждые 100 XP = новый курс = +50🪙

<b>💡 Совет:</b>
Следи за балансом! Не забывай есть и спать.

Удачи, студент! 🎓
"""
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

# ========== Обработчик данных из Mini App ==========

@router.message(lambda msg: msg.web_app_data is not None)
async def handle_webapp_data(message: types.Message):
    """Получение данных из Mini App"""
    try:
        data = message.web_app_data.data
        user = message.from_user
        
        logger.info(f"Получены данные от {user.id}: {data}")
        
        # Здесь можно обрабатывать данные из игры
        # Например, сохранение прогресса в БД
        
        await message.answer(
            "✅ Данные из игры получены!\n"
            "Прогресс синхронизирован с ботом.",
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки web_app_data: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке данных.\n"
            "Попробуй ещё раз.",
            reply_markup=get_main_keyboard()
        )

# ========== Настройка вебхуков ==========

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    # Устанавливаем вебхук
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logger.info(f"Webhook установлен: {WEBHOOK_URL}{WEBHOOK_PATH}")
    
    # Устанавливаем кнопку меню
    await bot.set_chat_menu_button(
        menu_button=types.MenuButtonWebApp(
            text="🎮 Играть",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )
    logger.info("Кнопка меню установлена")

async def on_shutdown(bot: Bot):
    """Действия при выключении бота"""
    # Удаляем вебхук
    await bot.delete_webhook()
    logger.info("Webhook удален")

def main():
    """Точка входа"""
    
    # Создаем приложение aiohttp
    app = web.Application()
    
    # Настройка вебхуков
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    # Регистрируем startup/shutdown
    app.on_startup.append(lambda _: on_startup(bot))
    app.on_shutdown.append(lambda _: on_shutdown(bot))
    
    # Запускаем сервер
    port = int(getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
