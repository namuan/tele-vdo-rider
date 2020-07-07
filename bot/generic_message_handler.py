import logging

from telegram.ext import MessageHandler, Filters

from yt import create_provider


class GenericMessageHandler:
    def __init__(self, dispatcher):
        self.video_link_handler = MessageHandler(
            Filters.text & (~Filters.command), self.create_video_provider
        )
        dispatcher.add_handler(self.video_link_handler)

    @staticmethod
    def create_video_provider(update, context):
        try:
            bot = context.bot
            cid = update.effective_chat.id
            video_link = update.message.text
            logging.info("Received message: {}".format(video_link))
            video_provider = create_provider(video_link, bot, cid)
            reply_message = bot.send_message(
                cid,
                "Managing request for : {}".format(video_link),
                disable_web_page_preview=True
            )
            video_provider.process(video_link, reply_message.message_id)
        except Exception as e:
            logging.error("Error processing request", e)
