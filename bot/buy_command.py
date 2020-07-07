from telegram import KeyboardButton, ReplyKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler

from config import market_summary_alt_coins
from exchanges import bittrex
from . import \
    WorkflowEnum, \
    KeyboardEnum, \
    restrict_access, \
    build_menu, \
    keyboard_cmds, \
    cancel, \
    regex_coin, \
    percent_change_buttons, \
    coin_buttons


def buy_setup(dispatcher):
    # BUY conversation handler
    chart_handler = ConversationHandler(
        entry_points=[CommandHandler('buy', buy_cmd, pass_chat_data=True)],
        states={
            WorkflowEnum.TRADE_CALCULATE_BUY_COST:
                [
                    RegexHandler("^(" + regex_coin(market_summary_alt_coins()) + ")$", calculate_buy_order_size,
                                 pass_chat_data=True),
                    RegexHandler("^(CANCEL)$", cancel)
                ],
            WorkflowEnum.TRADE_SELECT_BUY_ORDER_SIZE:
                [
                    RegexHandler("^\+(\d+)\%$", change_order_size, pass_chat_data=True, pass_groups=True),
                    RegexHandler("^([\d\.]+)\s+([\d\.]+)$", change_order_size, pass_chat_data=True,
                                 pass_groups=True),
                    RegexHandler("^(BUY)$", place_buy_order, pass_chat_data=True),
                    RegexHandler("^(CANCEL)$", cancel)
                ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(chart_handler)


@restrict_access
def buy_cmd(bot, update, chat_data):
    reply_msg = "Choose currency"

    cancel_btn = [
        KeyboardButton(KeyboardEnum.CANCEL.clean())
    ]

    reply_mrk = ReplyKeyboardMarkup(build_menu(coin_buttons(), n_cols=3, footer_buttons=cancel_btn),
                                    resize_keyboard=True)
    update.message.reply_text(reply_msg, reply_markup=reply_mrk)

    return WorkflowEnum.TRADE_CALCULATE_BUY_COST


def change_order_size(bot, update, chat_data, groups):
    minimum_quantity_to_buy = chat_data["minimum_quantity_to_buy"]
    coin_symbol = chat_data["coin_symbol"]
    ask_price = chat_data["buy_price"]
    existing_quantity = chat_data["quantity_to_buy"]

    if len(groups) > 1:  # manual quantity and price entry
        new_quantity_to_buy = float(groups[0])
        ask_price = float(groups[1])
    else:
        size_percent_change = float(groups[0])
        new_quantity_to_buy = existing_quantity + existing_quantity * (size_percent_change / 100)

    chat_data["minimum_quantity_to_buy"] = minimum_quantity_to_buy
    chat_data["quantity_to_buy"] = new_quantity_to_buy
    chat_data["buy_price"] = ask_price

    _, commission, total = bittrex.trade_commission(new_quantity_to_buy, ask_price)

    buttons = percent_change_buttons()
    buttons.append(KeyboardButton(KeyboardEnum.BUY.clean()))

    cancel_btn = [
        KeyboardButton(KeyboardEnum.CANCEL.clean())
    ]

    reply_msg = "*{}* order size changed.\n" \
                "New order size is *{:06.8f}*.\n" \
                "Ask is *{:06.8f}*.\n" \
                "Exchange commission will be *{:06.8f}*.\n" \
                "Total cost: *{:06.8f}*.\n" \
                "_Minimum order size is {:06.8f}._\n" \
                "Select different order size or place an order".format(
        coin_symbol,
        new_quantity_to_buy,
        ask_price,
        commission,
        total,
        minimum_quantity_to_buy
    )

    reply_mrk = ReplyKeyboardMarkup(build_menu(buttons, n_cols=2, footer_buttons=cancel_btn), resize_keyboard=True)
    update.message.reply_text(reply_msg, reply_markup=reply_mrk, parse_mode=ParseMode.MARKDOWN)

    return WorkflowEnum.TRADE_SELECT_BUY_ORDER_SIZE


def calculate_buy_order_size(bot, update, chat_data):
    currency = update.message.text
    coin_symbol = "BTC-{}".format(currency)

    price_info = bittrex.get_price(coin_symbol)
    if not price_info:
        return cancel(bot, update, "Unable to retrieve price for {}".format(coin_symbol))

    ask_price = price_info.get('Ask')

    minimum_exchange_trade_size = 0.00105000

    minimum_quantity_to_buy = minimum_exchange_trade_size / ask_price

    _, commission, total = bittrex.trade_commission(minimum_quantity_to_buy, ask_price)

    chat_data["minimum_quantity_to_buy"] = minimum_quantity_to_buy
    chat_data["coin_symbol"] = coin_symbol
    chat_data["quantity_to_buy"] = minimum_quantity_to_buy
    chat_data["buy_price"] = ask_price

    reply_msg = "{} minimum order size is {:06.8f}.\n" \
                "Ask is {:06.8f}.\n" \
                "Exchange commission will be {:06.8f}.\n" \
                "Total cost: {:06.8f}.\n" \
                "Select different order size or place an order".format(
        currency,
        minimum_quantity_to_buy,
        ask_price,
        commission,
        total
    )

    buttons = percent_change_buttons()
    buttons.append(KeyboardButton(KeyboardEnum.BUY.clean()))

    cancel_btn = [
        KeyboardButton(KeyboardEnum.CANCEL.clean())
    ]

    reply_mrk = ReplyKeyboardMarkup(build_menu(buttons, n_cols=2, footer_buttons=cancel_btn), resize_keyboard=True)
    update.message.reply_text(reply_msg, reply_markup=reply_mrk, parse_mode=ParseMode.MARKDOWN)

    return WorkflowEnum.TRADE_SELECT_BUY_ORDER_SIZE


def place_buy_order(bot, update, chat_data):
    coin_symbol = chat_data["coin_symbol"]
    quantity_to_buy = "{:06.4f}".format(chat_data["quantity_to_buy"])
    buy_price = "{:06.8f}".format(chat_data["buy_price"])

    order_id = bittrex.buy_order(
        quantity_to_buy=quantity_to_buy,
        trade_symbol=coin_symbol,
        buy_price=float(buy_price)
    )

    reply_msg = "Bought {} of {} at {}. Order Id: {}".format(
        quantity_to_buy,
        coin_symbol,
        buy_price,
        order_id
    )

    update.message.reply_text(reply_msg, reply_markup=keyboard_cmds())
    return ConversationHandler.END
