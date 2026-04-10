import asyncio
import logging
import sys
import json
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
BOT_TOKEN = getenv("BOT_TOKEN", "")
WEBHOOK_URL = getenv("WEBHOOK_URL", "https://your-app.bot-hosting.net")
WEBHOOK_PATH = "/webhook"
WEBAPP_URL = getenv("WEBAPP_URL", f"{WEBHOOK_URL}/web/")

# Проверка токена
if not BOT_TOKEN:
    logger.error("BOT_TOKEN не указан в переменных окружения!")
    sys.exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ========== Клавиатуры ==========

def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 ИГРАТЬ В ТАМАГОЧИ", web_app=WebAppInfo(url=WEBAPP_URL))
    builder.adjust(1)
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
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data="back_to_main")
    return builder.as_markup()

# ========== Обработчики ==========

@router.message(CommandStart())
async def command_start(message: types.Message):
    user = message.from_user
    user_name = user.first_name or "Студент"
    
    welcome_text = f"""
🎓 <b>Привет, {user_name}!</b>

Добро пожаловать в <b>Тамагочи-Общагу</b> — место, где ты можешь:
• 🛏️ Жить своей студенческой жизнью
• 📚 Учиться и прокачивать скиллы
• 🪙 Зарабатывать монеты
• 🥷 Воровать еду у соседей
• 🎉 Ходить на вписки

👇 Жми кнопку ниже, чтобы начать игру!
"""
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("🎮 <b>Главное меню</b>\n\nВыбери действие:", reply_markup=get_main_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "dorm")
async def show_dorm_info(callback: types.CallbackQuery):
    text = """
🏢 <b>ТВОЯ ОБЩАГА</b>

Соседи онлайн: <b>247 студентов</b>

Твои соседи по блоку:
• 🧑‍🎓 Макс (2 курс) — любит тусить
• 👩‍🎓 Аня (3 курс) — всегда учится
• 🧔‍♂️ Санёк (4 курс) — спит целыми днями

Совет: Можно стырить еду из общего холодильника!
"""
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "rating")
async def show_rating(callback: types.CallbackQuery):
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
"""
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "shop")
async def show_shop(callback: types.CallbackQuery):
    text = """
🛒 <b>МАГАЗИН ОБЩАГИ</b>

🍕 Доставка пиццы — 50 🪙
☕ Энергетик — 30 🪙
📚 Шпаргалки — 40 🪙
🎮 Приставка — 200 🪙
🛏️ Ортопедический матрас — 150 🪙

<i>Скоро в Mini App!</i>
"""
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()

@router.callback_query(lambda c: c.data == "help")
async def show_help(callback: types.CallbackQuery):
    text = """
ℹ️ <b>КАК ИГРАТЬ</b>

🎮 Основные действия:
• 🍽️ Поесть — 5🪙, +30 сытости
• 😴 Поспать — восстанавливает энергию
• 📝 Учёба — +15 к учёбе
• 💼 Подработка — +20-35🪙
• 🥷 Стырить еду — шанс 40%
• 🎉 Вписка — +40 настроения

⚡ Все показатели падают со временем!
"""
    await callback.message.edit_text(text, reply_markup=get_back_keyboard())
    await callback.answer()

@router.message(lambda msg: msg.web_app_data is not None)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        user = message.from_user
        logger.info(f"Данные от {user.id}: coins={data.get('coins')}, level={data.get('level')}")
        
        await message.answer(
            f"✅ Прогресс сохранён!\n"
            f"💰 Монет: {data.get('coins', 0)}\n"
            f"🎓 Курс: {data.get('level', 1)}",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Ошибка сохранения", reply_markup=get_main_keyboard())

# ========== Вебхуки ==========

async def on_startup(bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logger.info(f"Webhook: {WEBHOOK_URL}{WEBHOOK_PATH}")
    
    await bot.set_chat_menu_button(
        menu_button=types.MenuButtonWebApp(
            text="🎮 Играть",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )
    )

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

def main():
    app = web.Application()
    
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    app.on_startup.append(lambda _: on_startup(bot))
    app.on_shutdown.append(lambda _: on_shutdown(bot))
    
    port = int(getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
