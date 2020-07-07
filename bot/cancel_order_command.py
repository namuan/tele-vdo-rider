from telegram import ParseMode
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler

from exchanges import bittrex
from . import WorkflowEnum
from . import \
    restrict_access, \
    cancel, \
    keyboard_confirm, \
    keyboard_cmds, \
    KeyboardEnum


def cancel_order_setup(dispatcher):
    # CANCEL ORDER conversation handler
    cancel_order_handler = ConversationHandler(
        entry_points=[CommandHandler('cancel', cancel_order_cmd, pass_chat_data=True)],
        states={
            WorkflowEnum.ORDER_CANCEL:
                [
                    RegexHandler("^(YES|NO)$", order_cancel, pass_chat_data=True)
                ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(cancel_order_handler)


# Show the last trade price for a currency
@restrict_access
def cancel_order_cmd(bot, update, chat_data):
    selected_order = chat_data["selected_order"]
    if not selected_order:
        return cancel(bot, update, "No selected order")

    order_text = chat_data[selected_order].get('order_text')
    update.message.reply_text(
        "Are you sure about cancelling {}?".format(order_text),
        reply_markup=keyboard_confirm(), parse_mode=ParseMode.MARKDOWN)

    return WorkflowEnum.ORDER_CANCEL


def order_cancel(bot, update, chat_data):
    if update.message.text == KeyboardEnum.NO.clean():
        return cancel(bot, update)

    selected_order = chat_data["selected_order"]
    order_text = chat_data[selected_order].get('order_text')

    bittrex.cancel_order(order_id=selected_order)

    update.message.reply_text(
        "Canceling order: {} with order id: {}".format(order_text, selected_order),
        reply_markup=keyboard_cmds(), parse_mode=ParseMode.MARKDOWN)

    # Reset chat_data
    chat_data["selected_order"] = None

    return ConversationHandler.END
