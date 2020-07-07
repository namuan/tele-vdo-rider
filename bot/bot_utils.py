import logging

from telegram import KeyboardButton

from config import bot_cfg


# Decorator to restrict access if user is not the same as in config
def restrict_access(func):
    def _restrict_access(bot, update, chat_data):
        chat_id = get_chat_id(update)
        if str(chat_id) != bot_cfg("TELEGRAM_USER_ID"):
            # Inform owner of bot
            msg = "Access denied for user %s" % chat_id
            bot.send_message(bot_cfg("TELEGRAM_USER_ID"), text=msg)

            logging.info(msg)
            return
        else:
            return func(bot, update, chat_data)

    return _restrict_access


# Return chat ID for an update object
def get_chat_id(update=None):
    if update.message:
        return update.message.chat_id
    elif update.callback_query:
        return update.callback_query.from_user["id"]


# Remove trailing zeros to get clean values
def trim_zeros(value_to_trim):
    if isinstance(value_to_trim, float):
        return ('%.8f' % value_to_trim).rstrip('0').rstrip('.')
    elif isinstance(value_to_trim, str):
        str_list = value_to_trim.split(" ")
        for i in range(len(str_list)):
            old_str = str_list[i]
            if old_str.replace(".", "").isdigit():
                new_str = str(('%.8f' % float(old_str)).rstrip('0').rstrip('.'))
                str_list[i] = new_str
        return " ".join(str_list)
    else:
        return value_to_trim


# Add asterisk as prefix and suffix for a string
# Will make the text bold if used with Markdown
def bold(text):
    return "*" + text + "*"


# Handle all telegram and telegram.ext related errors
def handle_telegram_error(update, error):
    error_str = "Update '%s' caused error '%s'" % (update, error)
    logging.error(error_str)


def regex_coin(coins):
    coins_regex_or = str()

    for coin in coins:
        coins_regex_or += coin + "|"

    return coins_regex_or[:-1]


def percent_change_buttons():
    buttons = list()
    for pct in ['1', '2', '5', '10', '20', '50', '100']:
        buttons.append(KeyboardButton("+{}%".format(pct)))

    return buttons


def track_order_pct_change_buttons():
    buttons = list()
    for pct in ['1', '2', '50', '10']:
        buttons.append(KeyboardButton("+{}%".format(pct)))
        buttons.append(KeyboardButton("-{}%".format(pct)))

    return buttons
