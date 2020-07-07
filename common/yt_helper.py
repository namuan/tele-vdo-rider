#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

import requests
import youtube_dl as ytdl


WORKING_DIRECTORY_ABS_PATH = os.path.abspath('.')
AUDIO_OUTPUT_DIR_NAME = 'output_dir'
AUDIO_OUTPUT_DIR = os.path.join(WORKING_DIRECTORY_ABS_PATH, AUDIO_OUTPUT_DIR_NAME)
OUTPUT_FORMAT = os.path.join(AUDIO_OUTPUT_DIR, '%(id)s.%(ext)s')
PREFERRED_AUDIO_CODEC = 'mp3'


def rename_file(old_filename, new_filename):
    full_path, filename = os.path.split(old_filename)
    filename, extension = os.path.splitext(filename)
    temp_filename = os.path.join(full_path, new_filename + extension)
    os.rename(old_filename, temp_filename)
    return temp_filename


def format_size(size):
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


class FileIsTooLargeException(ValueError):
    pass


class DownloadError(ValueError):
    pass


class YoutubeDLLogger(object):
    def debug(self, msg):
        logging.debug('[def debug] ' + msg)

    def warning(self, msg):
        logging.warning('[def warning] ' + msg)

    def error(self, msg):
        logging.error('[def error] ' + msg)


class YoutubeVideo(object):
    YOUTUBE_WATCH_URL = 'https://www.youtube.com/watch?v=%s'

    def __str__(self):
        return ('%s (%s)' % (self.get_video_title(), self.get_url())).encode('utf8', 'replace')

    def __init__(self, video_id, info, progress_hook):
        self._DOWNLOAD_VIDEO_AND_EXTRACT_AUDIO = {
            'outtmpl': OUTPUT_FORMAT,
            'format': 'bestaudio/best',
            'socket_timeout': 10,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': PREFERRED_AUDIO_CODEC,
                'preferredquality': '192',
            }],
            'retries': 10,
            'logger': YoutubeDLLogger(),
            'progress_hooks': [self._private_progress_hook],
            'prefer_ffmpeg': True
        }

        self._video_id = video_id
        self._info = info
        self._progress_hook = progress_hook

    def _private_progress_hook(self, hook):
        self._progress_hook(hook, youtube_video=self)

    def get_url(self):
        return self.YOUTUBE_WATCH_URL % self._video_id

    def get_type(self):
        return self._info['extractor']

    def get_youtube_id(self):
        return self._video_id

    def get_video_title(self):
        return self._info['title']

    def get_video_thumbnails(self):
        return map(lambda x: x['url'], self._info['thumbnails'])

    def download_thumbnail(self, index):
        thumbnail = self.get_video_thumbnails()[index]
        output = os.path.abspath(os.path.join(AUDIO_OUTPUT_DIR, 'thumb_{0}'.format(self.get_youtube_id())))

        r = requests.get(thumbnail, stream=True)
        if r.status_code == 200:
            with open(output, 'wb') as f:
                for chunk in r:
                    f.write(chunk)

        class Thumbnail(object):
            def __init__(self, url, filename, mimetype):
                self.url = url
                self.filename = filename
                self.mimetype = mimetype

        return Thumbnail(thumbnail, output, r.headers['Content-Type'])

    def is_part_of_playlist(self):
        return self._info['playlist_index'] is not None

    def _get_downloaded_file_abspath(self):
        filename = self.get_youtube_id() + '.' + PREFERRED_AUDIO_CODEC
        return os.path.abspath(os.path.join(AUDIO_OUTPUT_DIR, filename))

    def download_video_and_extract_audio(self):
        logging.info("Starting download: {} ({})".format(self.get_video_title(), self.get_url()))
        try:
            ydl = ytdl.YoutubeDL(self._DOWNLOAD_VIDEO_AND_EXTRACT_AUDIO)
            ydl.download([self.get_url()])

            self._progress_hook({
                'status': 'searching_metadata'
            }, youtube_video=self)

            target_file_name = "target_file_name"

            logging.debug(self._get_downloaded_file_abspath())
            logging.debug('{0}_{1}'.format(target_file_name, self.get_youtube_id()))

            filename = rename_file(self._get_downloaded_file_abspath(),
                                   '{0}_{1}'.format(target_file_name, self.get_youtube_id()))

            # if the extracted audio file is larger than 50M
            filesize = os.path.getsize(filename)
            if filesize >> 20 > 50:
                raise FileIsTooLargeException(
                    'I am sorry. Telegram bots can currently send files of any type of up to 50 MB in size. '
                    'https://core.telegram.org/bots/faq#how-do-i-upload-a-large-file\n '
                    'This audio file is %s!' % format_size(filesize))

            return {
                'title': self.get_video_title(),
                'author': 'metadata.author',
                'album': 'metadata.album',
                'track_number': 'metadata.track_number',
                'first_release_date': 'metadata.first_release_date',
                'filename': filename
            }
        except ytdl.utils.DownloadError as e:
            raise DownloadError('Failed downloading video: %s\n%s' % (self.__str__(), e))


class YTHelper(object):
    def __init__(self, url, progress_hook):
        self._url = url
        self._progress_hook = progress_hook
        self._INFO_OPTS = {
            'logger': YoutubeDLLogger(),
            'socket_timeout': 10
        }

        ydl = ytdl.YoutubeDL(self._INFO_OPTS)
        self._progress_hook({
            'status': 'getting_information'
        })
        self._info = ydl.extract_info(self._url, download=False)
        self._progress_hook({
            'status': 'information_downloaded',
            'type': 'playlist' if self.is_playlist() else 'video'
        })
        logging.info("Video Info: {}".format(self.get_info()))

    def get_info(self):
        return self._info

    def get_type(self):
        return self._info['extractor']

    def get_youtube_id(self):
        return self._info['id']

    def is_playlist(self):
        if 'playlist' in self.get_type():
            return True
        return False

    def manage_url(self):
        if not self.is_playlist():
            yield YoutubeVideo(self.get_youtube_id(), self.get_info(), self._progress_hook)
        else:
            for entry in self.get_info()['entries']:
                yield YoutubeVideo(entry['id'], entry, self._progress_hook)


if __name__ == '__main__':
    links = [
        'https://www.youtube.com/shared?ci=teeR9PxnJG0',
        'https://www.youtube.com/watch?v=PDSkFeMVNFs',
        'https://www.youtube.com/watch?v=FfbZfBk-3rI',
        'https://www.youtube.com/playlist?list=PL5jc9xFGsL8E12so1wlMS0r0hTQoJL74M',
        'https://www.youtube.com/watch?v=LL8wkskDlbs&index=1&list=PL5jc9xFGsL8E12so1wlMS0r0hTQoJL74M',
        'https://www.youtube.com/watch?v=wGyUP4AlZ6I',
        'https://www.youtube.com/watch?v=ytWz0qVvBZ0',
        'https://www.youtube.com/playlist?list=PL7E7D54D2B79C2D41',
        'http://youtu.be/NLqAF9hrVbY',
        'https://www.youtube.com/shared?ci=teeR9PxnJG0',
        'http://www.youtube.com/embed/NLqAF9hrVbY',
        'https://www.youtube.com/embed/NLqAF9hrVbY',
        'http://www.youtube.com/v/NLqAF9hrVbY?fs=1&hl=en_US',
        'http://www.youtube.com/watch?v=NLqAF9hrVbY',
        'http://www.youtube.com/watch?v=JYArUl0TzhA&feature=featured',
        'https://www.youtube.com/watch?v=a01QQZyl-_I&index=1&list=PLJ8y7DDcrI_p8LixOD4nVgrr9P6f4n2Lv',
        'https://youtu.be/a01QQZyl-_I?list=PLJ8y7DDcrI_p8LixOD4nVgrr9P6f4n2Lv',
        'https://www.youtube.com/watch?v=LL8wkskDlbs&index=1&list=PL5jc9xFGsL8E12so1wlMS0r0hTQoJL74M',
        # errors
        'https://www.youube.com/watch?v=qy1Fzem7mqA',
        'https://www.youtube.com/playlist?list=PL5jc9xFGsL8E12so1wlMS0r0hTQoJL74M',
    ]
