import logging
import os

import youtube_dl as yt

from bot.exceptions import FileIsTooLargeException
from bot.mp3_splitter import Mp3Splitter
from common.helper import format_size, rename_file
from config.bot_config import PREFERRED_AUDIO_CODEC, AUDIO_OUTPUT_DIR
from config import bot_cfg

split_file = int(bot_cfg("SPLIT_FILE", 0))  # 0 == False


class AudioRequestHandler:
    def __init__(self, extraction_param, notifier):
        self.extraction_param = extraction_param
        self.notifier = notifier
        self.video_info = None

    def get_downloaded_file_abspath(self):
        filename = self.video_id() + "." + PREFERRED_AUDIO_CODEC
        return os.path.abspath(os.path.join(AUDIO_OUTPUT_DIR, filename))

    def video_id(self):
        return self.video_info["id"]

    def video_title(self):
        return self.video_info["title"]

    def video_url(self):
        return self.video_info["webpage_url"]

    def process_video(self, yt_video):
        self.video_info = yt_video
        ydl = yt.YoutubeDL(self.extraction_param)
        ydl.download([self.video_url()])
        downloaded_filename = self.get_downloaded_file_abspath()
        file_size = os.path.getsize(downloaded_filename)
        formatted_file_size = format_size(file_size)
        downloaded_video_message = "🔈 File size: {}".format(formatted_file_size)
        self.notifier.progress_update(downloaded_video_message)
        logging.info(downloaded_video_message)

        filename = rename_file(
            self.get_downloaded_file_abspath(),
            "{0}_{1}".format(self.video_title(), self.video_id()),
        )

        # if the extracted audio file is larger than 50M
        allowed_file_size = 50
        if file_size >> 20 > allowed_file_size:
            file_size_warning = "😱 File size {} > allowed {} therefore trying to chunk into smaller files".format(
                formatted_file_size, allowed_file_size
            )
            self.notifier.progress_update(file_size_warning)
            logging.info(file_size_warning)

            if bool(split_file):
                mp3_splitter = Mp3Splitter(filename)
                for chunk_filename in mp3_splitter.split_chunks():
                    yield {"filename": chunk_filename}
            else:
                raise FileIsTooLargeException(
                    "File too big to transfer. Copy with FTP/SFTP"
                )
        else:
            yield {
                "filename": filename,
            }
