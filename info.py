from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    API_ID = int(getenv("API_ID", "0"))
    API_HASH = getenv("API_HASH", "")
    BOT_TOKEN = getenv("BOT_TOKEN", "")
    BOT_WORKERS = int(getenv("BOT_WORKERS", "4"))
    
    # Webhook settings
    WEB_MODE = getenv("WEB_MODE", "False").lower() in ("true", "1", "yes")
    PORT = int(getenv("PORT", "8080"))  # default port for web services
    
    CHANNEL_ID = int(getenv("CHANNEL_ID", ""))
    OWNER_ID = int(getenv("OWNER_ID", ""))

    # Database
    DATABASE_URL = getenv("DATABASE_URL", "")
    DATABASE_NAME = getenv("DATABASE_NAME", "Cluster0")

    # Force subscription
    FORCE_SUB_CHANNEL = int(getenv("FORCE_SUB_CHANNEL", "0"))
    JOIN_REQUEST_ENABLE = getenv("JOIN_REQUEST_ENABLED", None)

    # Messages
    START_PIC = getenv("START_PIC", "")
    START_MSG = getenv("START_MESSAGE", "👋 Hello {mention},\n\nThis bot helps you store private files in a secure channel and generate special access links for sharing. 🔐📁\n\nOnly admins can upload files and generate links. Just send the file here to get started.")
    FORCE_MSG = getenv("FORCE_SUB_MESSAGE", "👋 Hello {mention},\n\n<b>You need to join our updates channel before using this bot.</b>\n\n📢 Please join the required channel, then try again.")
    CUSTOM_CAPTION = getenv("CUSTOM_CAPTION", None)

    # ✅ Secure ADMINS (only numeric IDs)
    admins = getenv("ADMINS", "").split()
    ADMINS = list(set(
        [int(x) for x in admins if x.isdigit()] + [OWNER_ID]
    ))

    # Other configs
    PROTECT_CONTENT = getenv("PROTECT_CONTENT", "False") == "True"
    DISABLE_CHANNEL_BUTTON = getenv("DISABLE_CHANNEL_BUTTON", "False") == "True"

    AUTO_DELETE_TIME = int(getenv("AUTO_DELETE_TIME", "0"))
    AUTO_DELETE_MSG = getenv("AUTO_DELETE_MSG", "This file will be automatically deleted in {time} seconds.")
    AUTO_DEL_SUCCESS_MSG = getenv("AUTO_DEL_SUCCESS_MSG", "✅ File deleted successfully.")

    BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
    USER_REPLY_TEXT = "❌ I'm a bot — please don't DM me!"
