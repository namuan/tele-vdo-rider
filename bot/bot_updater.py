from telegram.ext import Updater

from config import bot_cfg

# Set bot token, get dispatcher and job queue
bot_token = bot_cfg("TELEGRAM_BOT_TOKEN")
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher
