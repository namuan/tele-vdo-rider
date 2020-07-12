import glob
import os
import subprocess

from config import bot_cfg

split_time = bot_cfg("SPLIT_TIME_FOR_OVERSIZED_FILES")


class Mp3Splitter(object):
    def __init__(self, original_file_path):
        self.original_file_path = original_file_path
        self.file_directory = os.path.dirname(original_file_path)
        self.file_name = os.path.basename(original_file_path)

    def split_chunks(self):
        subprocess.call(
            'mp3splt -t {} -o "@n @f" "{}"'.format(split_time, self.original_file_path),
            shell=True,
        )
        os.remove(self.original_file_path)
        return [f for f in glob.glob("{}/* {}".format(self.file_directory, self.file_name))]
