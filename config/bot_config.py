import configparser
import os
from pathlib import Path

AUDIO_OUTPUT_DIR = Path("~/OutputDir").expanduser().joinpath("videos-to-mp3")
OUTPUT_FORMAT = os.path.join(AUDIO_OUTPUT_DIR, "%(id)s.%(ext)s")
PREFERRED_AUDIO_CODEC = "mp3"


def config(key, default_value=None):
    c = configparser.ConfigParser()
    c.read("env.cfg")

    return c.get("ALL", key) or default_value
