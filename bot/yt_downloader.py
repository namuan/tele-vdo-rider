import logging
import re

from emoji import emojize
from telegram.ext import MessageHandler, Filters

from common.yt_helper import YTHelper, DownloadError, FileIsTooLargeException

YOUTUBE_REGEX = '^((http(s)?:\/\/)?)(www\.)?(m\.)?((youtube\.com\/)|(youtu.be\/))[\S]+'


class TelegramProgressNotifier(object):
    STATUS_TO_MESSAGE = {
        'getting_information': lambda h: 'Getting video information',
        'information_downloaded': lambda h: 'Information retrieved! Starting download the %s..' % h['type'],
        'already_downloaded': lambda h: 'Audio found in the database. Already downloaded %d %s' %
                                        (h['downloaded_times'], 'time' if h['downloaded_times'] == 1 else 'times'),
        'downloading': lambda h: '[%s] Downloading at %s' % (h['_percent_str'], h['_speed_str']),
        'finished': lambda h: 'Download finished: %s\nStart extracting audio postprocess..' % h['_total_bytes_str'],
        'searching_metadata': lambda h: 'Searching audio metadata from Spotify and Musixmatch',
        'upload_audio': lambda h: 'Uploading...',
        'done': lambda h: emojize('Done! :white_heavy_check_mark:')
    }

    def __init__(self, bot, chat_id, message_id):
        self._bot = bot
        self._chat_id = chat_id
        self._message_id = message_id
        self._count = 0

    def get_progress_hook(self):
        return self._update_notifier

    def notify_progress(self, hook):
        self._update_notifier(hook)

    def _update_notifier(self, hook, youtube_video=None):
        try:
            text = ''
            if youtube_video:
                text += '%s\n%s\n\n' % (youtube_video.get_video_title(), youtube_video.get_url())

            text += self.STATUS_TO_MESSAGE[hook['status']](hook)

            self._bot.edit_message_text(text, self._chat_id, self._message_id, disable_web_page_preview=True)
            # self._bot.send_message(self._chat_id, text, disable_web_page_preview=True)
        except KeyError as e:
            self._bot.send_message(self._chat_id, str(e))


def process_yt_videos(update, context):
    bot = context.bot
    cid = update.effective_chat.id
    yt_link = update.message.text
    logging.info("Received message: {}".format(update.message.text))
    # Extract youtube video id from yt_link
    r = re.search(YOUTUBE_REGEX, yt_link)
    try:
        if r is not None:
            youtube_url = r.group(0)
            reply_message = bot.send_message(cid, 'Managing your request...')
            tg_progress_notifier = TelegramProgressNotifier(bot, cid, reply_message.message_id)
            yt_helper = YTHelper(youtube_url, tg_progress_notifier.get_progress_hook())

            for ytvideo in yt_helper.manage_url():
                try:
                    data = ytvideo.download_video_and_extract_audio()
                    audio = open(data['filename'], 'rb')
                    tg_progress_notifier.notify_progress({
                        'status': 'upload_audio'
                    })
                    bot.send_chat_action(cid, 'upload_audio')
                    bot.send_audio(cid, audio, caption='Downloaded using @podtubebot')
                except DownloadError as e:
                    logging.error('[Download Error] %s', e)
                    bot.send_message(cid, str(e))
                except FileIsTooLargeException as e:
                    logging.error('[File Is Too Large] %s', e)
                    bot.send_message(cid, str(e), disable_web_page_preview=True)

            tg_progress_notifier.notify_progress({
                'status': 'done'
            })
        else:
            context.bot.send_message(cid, 'Sorry, it is not a valid youtube link!')
    except Exception as e:
        logging.error('Error', e)
        bot.send_message(cid, str(e), disable_web_page_preview=True)
        raise e


def yt_command_setup(dispatcher):
    yt_video_link_handler = MessageHandler(Filters.text & (~Filters.command), process_yt_videos)
    dispatcher.add_handler(yt_video_link_handler)
