import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (для локальной разработки)
load_dotenv()

# Токен бота из BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "8054662227:AAFCEUkLrAtk0fgBjuDAqoeTPoiq2Vu1idk")

# URL для вебхука (выдаст BotHost после деплоя)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-bot-host-url.com")
WEBHOOK_PATH = "/webhook"

# URL Mini App (там где лежит HTML/JS)
# Если Mini App лежит в папке web/ на том же хостинге
WEBAPP_URL = os.getenv("WEBAPP_URL", f"{WEBHOOK_URL}/web/")
