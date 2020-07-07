import logging

import youtube_dl as yt
from emoji import emojize

from bot.exceptions import FileIsTooLargeException
from bot.telegram_notifier import TelegramNotifier
from yt.youtube_audio_request_handler import YoutubeAudioRequestHandler


class YoutubeVideo:
    def __init__(self, video_info):
        self.info = video_info


class YoutubeVideoProvider:

    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.video_info = None

    def process(self, video_link, update_message_id):
        notifier = TelegramNotifier(self.bot, self.chat_id, update_message_id)
        yt_downloader = yt.YoutubeDL({"socket_timeout": 10})
        self.video_info = yt_downloader.extract_info(video_link, download=False)
        notifier.progress_update("Processing video")
        request_handler = YoutubeAudioRequestHandler(notifier)
        try:
            for yt_video in self.yt_videos():
                logging.info("Processing Video -> {}".format(yt_video.info))
                data = request_handler.process_video(video_link, yt_video.info)
                audio = open(data["filename"], "rb")
                notifier.progress_update("Uploading audio")
                self.bot.send_chat_action(self.chat_id, "upload_audio")
                self.bot.send_audio(self.chat_id, audio, caption="Downloaded using @podtubebot", timeout=60)
        except FileIsTooLargeException as e:
            logging.error("[File Is Too Large] %s", e)
            self.bot.send_message(self.chat_id, str(e), disable_web_page_preview=True)

        notifier.progress_update(emojize("Done! :white_heavy_check_mark:"))

    def yt_videos(self):
        if not self.is_yt_playlist():
            yield YoutubeVideo(self.video_info)
        else:
            for entry in self.get_playlist_videos():
                yield YoutubeVideo(entry)

    def is_yt_playlist(self):
        if "playlist" in self.get_type():
            return True
        return False

    def get_playlist_videos(self):
        return self.video_info["entries"]

    def get_type(self):
        return self.video_info["extractor"]
