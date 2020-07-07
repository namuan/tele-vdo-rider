import logging
import os

import youtube_dl as yt

from bot.exceptions import FileIsTooLargeException
from common.helper import format_size, rename_file

WORKING_DIRECTORY_ABS_PATH = os.path.abspath(".")
AUDIO_OUTPUT_DIR_NAME = "output_dir"
AUDIO_OUTPUT_DIR = os.path.join(WORKING_DIRECTORY_ABS_PATH, AUDIO_OUTPUT_DIR_NAME)
OUTPUT_FORMAT = os.path.join(AUDIO_OUTPUT_DIR, "%(id)s.%(ext)s")
PREFERRED_AUDIO_CODEC = "mp3"


class YoutubeAudioRequestHandler:
    EXTRACT_AUDIO_PARAMS = {
        "outtmpl": OUTPUT_FORMAT,
        "format": "bestaudio/best",
        "socket_timeout": 10,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": PREFERRED_AUDIO_CODEC,
                "preferredquality": "192",
            }
        ],
        "retries": 10,
        "prefer_ffmpeg": True,
        "keepvideo": True,
    }

    def __init__(self, notifier):
        self.notifier = notifier
        self.video_info = None

    def get_downloaded_file_abspath(self):
        filename = self.video_id() + "." + PREFERRED_AUDIO_CODEC
        return os.path.abspath(os.path.join(AUDIO_OUTPUT_DIR, filename))

    def video_id(self):
        return self.video_info["id"]

    def video_title(self):
        return self.video_info["title"]

    def process_video(self, video_link, yt_video):
        self.video_info = yt_video
        ydl = yt.YoutubeDL(self.EXTRACT_AUDIO_PARAMS)
        ydl.download([video_link])
        downloaded_filename = self.get_downloaded_file_abspath()
        file_size = os.path.getsize(downloaded_filename)
        formatted_file_size = format_size(file_size)
        downloaded_video_message = "File size: {}".format(formatted_file_size)
        self.notifier.progress_update(downloaded_video_message)
        logging.info(downloaded_video_message)

        filename = rename_file(
            self.get_downloaded_file_abspath(),
            "{0}_{1}".format(self.video_title(), self.video_id()),
        )

        # if the extracted audio file is larger than 50M
        if file_size >> 20 > 50:
            raise FileIsTooLargeException(
                "Bots can currently send files of any type of up to 50 MB in size\n "
                "https://core.telegram.org/bots/faq#how-do-i-upload-a-large-file\n "
                "This audio file is {}!".format(formatted_file_size)
            )

        return {
            "title": self.video_title(),
            "filename": filename,
        }
