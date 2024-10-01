import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))
GROUP_ID = os.getenv("GROUP_ID")
