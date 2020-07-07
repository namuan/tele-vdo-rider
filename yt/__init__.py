import re

from .youtube_video_provider import YoutubeVideoProvider

YOUTUBE_REGEX = "^((http(s)?:\/\/)?)(www\.)?(m\.)?((youtube\.com\/)|(youtu.be\/))[\S]+"


def create_provider(video_link, bot, cid):
    r = re.search(YOUTUBE_REGEX, video_link)
    if r is not None:
        return YoutubeVideoProvider(bot, cid)
    else:
        bot.send_message(cid, "Invalid data \'{}\' Make sure that you are sending Youtube link".format(video_link))
        return None
