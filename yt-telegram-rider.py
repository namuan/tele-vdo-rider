#!/usr/bin/python3
"""
python3 yt-telegram-rider.py
"""
from telegram.ext import CommandHandler

from bot import *

dispatcher.add_error_handler(handle_telegram_error)

# Add command handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start_cmd))
dispatcher.add_handler(CommandHandler("restart", restart_cmd, pass_chat_data=True))
dispatcher.add_handler(CommandHandler("shutdown", shutdown_cmd, pass_chat_data=True))

yt_command_setup(dispatcher)

updater.start_polling()

start_cmd(updater)

updater.idle()
