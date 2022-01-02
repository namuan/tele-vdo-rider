import logging

from telegram.ext import MessageHandler, Filters

from bot.video_provider import VideoProvider


class GenericMessageHandler:
    def __init__(self, dispatcher):
        self.video_link_handler = MessageHandler(
            Filters.text & (~Filters.command), self.create_video_provider
        )
        dispatcher.add_handler(self.video_link_handler)

    @staticmethod
    def create_video_provider(update, context):
        bot = context.bot
        cid = update.effective_chat.id
        video_link = update.message.text
        logging.info("Received message: {}".format(video_link))
        try:
            video_provider = VideoProvider(bot, cid)
            reply_message = bot.send_message(
                cid,
                "Got it. 👀 at 📼".format(video_link),
                disable_web_page_preview=True,
            )
            video_provider.process(video_link, reply_message.message_id)
            bot.delete_message(cid, reply_message.message_id)
            logging.info("Finished processing {}".format(video_link))
        except Exception as e:
            bot.send_message(
                "🆘 Looks like something went wrong. "
                "\nWe'll have a look and try to fix this issue."
            )
            logging.exception(
                "Error processing request for {} and video link: {}".format(
                    cid, video_link
                ),
            )
