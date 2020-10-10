import enum
import datetime
import logging
import os
import shutil
import subprocess
import time
import pykka
import requests

import config


class Ffmpeg(pykka.ThreadingActor):
    def __init__(self, channel: str):
        super().__init__()
        self._in_future = self.actor_ref.proxy()

        self._channel: str = channel
        self._ffmpeg_path = "ffmpeg"

        self._root_path = config.root_path
        self._record_path = config.recorded_path

        # path to finished video, errors removed
        self._processed_path = os.path.join(self._root_path, "processed", self._channel)
        # path to recorded stream
        self._recorded_path = os.path.join(self._record_path, "recorded", self._channel)

        # create directory for processedPath if not exist
        if not os.path.isdir(self._processed_path):
            os.makedirs(self._processed_path)

        logging.info("Created ffmpeg for channel: %s", channel)

    def _ffmpeg_copy_and_fix_errors(self, recorded_filename, processed_filename):
        try:
            subprocess.call(
                [self._ffmpeg_path, "-err_detect", "ignore_err", "-i", recorded_filename, "-c", "copy",
                 processed_filename])
            os.remove(recorded_filename)
        except Exception as e:
            logging.error(e)

    def fix(self, recorded_filename, filename, is_file_name=False):
        processed_filename = filename
        if is_file_name:
            processed_filename = os.path.join(self._processed_path, filename)
        logging.info("Fixing file: %s", recorded_filename)
        self._ffmpeg_copy_and_fix_errors(recorded_filename, processed_filename)

    def fix_all(self):
        try:
            video_list = [f for f in os.listdir(self._recorded_path) if os.path.isfile(os.path.join(self._recorded_path, f))]
            if len(video_list) > 0:
                logging.info("processing previously recorded files")
            for f in video_list:
                recorded_filename = os.path.join(self._recorded_path, f)
                processed_filename = os.path.join(self._processed_path, f)
                self._in_future.fix(recorded_filename, processed_filename, False)
        except Exception as e:
            logging.error(e)








