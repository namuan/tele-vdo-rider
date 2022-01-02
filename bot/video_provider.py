import logging
import os
import youtube_dl as yt

from bot.audio_extraction_params import create_audio_extraction_params
from bot.exceptions import FileIsTooLargeException
from bot.telegram_notifier import TelegramNotifier


class Video:
    def __init__(self, video_info):
        self.info = video_info


class VideoProvider:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id
        self.video_info = None

    def process(self, video_link, update_message_id):
        notifier = TelegramNotifier(self.bot, self.chat_id, update_message_id)
        yt_downloader = yt.YoutubeDL({"socket_timeout": 10})
        self.video_info = yt_downloader.extract_info(video_link, download=False)
        notifier.progress_update("‍🤖 processing video")
        request_handler = create_audio_extraction_params(
            self.video_info.get("extractor"), notifier
        )
        try:
            for yt_video in self.yt_videos():
                logging.info("Processing Video -> {}".format(yt_video.info))
                for data in request_handler.process_video(yt_video.info):
                    filename = data["filename"]
                    audio = open(filename, "rb")

                    notifier.progress_update(
                        "Almost there. Uploading {} 🔈".format(
                            os.path.basename(filename)
                        )
                    )

                    self.bot.send_chat_action(self.chat_id, "upload_audio")
                    self.bot.send_audio(
                        self.chat_id,
                        audio,
                        caption="Downloaded using @podtubebot",
                        timeout=120,
                    )
        except FileIsTooLargeException as e:
            logging.error("[File Is Too Large] %s", e)
            self.bot.send_message(self.chat_id, str(e), disable_web_page_preview=True)
        except Exception as e:
            logging.exception("Something bad happened: %s", e)
            self.bot.send_message(self.chat_id, str(e), disable_web_page_preview=True)

        notifier.progress_update("Done! ✅")

    def yt_videos(self):
        if not self.is_yt_playlist():
            yield Video(self.video_info)
        else:
            for entry in self.get_playlist_videos():
                yield Video(entry)

    def is_yt_playlist(self):
        if "playlist" in self.get_type():
            return True
        return False

    def get_playlist_videos(self):
        return self.video_info["entries"]

    def get_type(self):
        return self.video_info["extractor"]
