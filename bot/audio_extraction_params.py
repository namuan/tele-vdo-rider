from config.bot_config import OUTPUT_FORMAT, PREFERRED_AUDIO_CODEC
from bot.audio_request_handler import AudioRequestHandler

YOUTUBE_REGEX = "^((http(s)?:\/\/)?)(www\.)?(m\.)?((youtube\.com\/)|(youtu.be\/))[\S]+"

YOUTUBE_EXTRACT_AUDIO_PARAMS = {
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

SOUND_CLOUD_EXTRACT_AUDIO_PARAMS = {
    "outtmpl": OUTPUT_FORMAT,
    "format": "bestaudio/best",
    "socket_timeout": 10,
    "retries": 10,
    "prefer_ffmpeg": True,
    "keepvideo": True,
}


def create_audio_extraction_params(video_extractor, notifier):
    extraction_param = (
        SOUND_CLOUD_EXTRACT_AUDIO_PARAMS
        if is_sound_cloud_video(video_extractor)
        else YOUTUBE_EXTRACT_AUDIO_PARAMS
    )
    return AudioRequestHandler(extraction_param, notifier)


def is_yt_video(extractor):
    return extractor is "youtube"


def is_sound_cloud_video(extractor):
    return extractor is "soundcloud"
