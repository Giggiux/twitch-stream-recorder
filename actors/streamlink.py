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


class Streamlink(pykka.ThreadingActor):
    def __init__(self, channel: str, access_token: str, client_id: str):
        super().__init__()
        self._in_future = self.actor_ref.proxy()

        self._channel: str = channel
        self._access_token: str = access_token
        self._client_id: str = client_id
        self._quality: str = "best"

        self._record_path = config.recorded_path

        # path to recorded stream
        self._recorded_path = os.path.join(self._record_path, "recorded", self._channel)

        # create directory for recordedPath if not exist
        if not os.path.isdir(self._recorded_path):
            os.makedirs(self._recorded_path)

        print("Created StreamLink for channel: %s", channel)

    def record(self, info):
        logging.info("%s online, stream recording in session", self._channel)

        channels = info["data"]
        channel = next(iter(channels), None)
        filename = self._channel + " - " + datetime.datetime.now() \
            .strftime("%Y-%m-%d %Hh%Mm%Ss") + " - " + channel.get("title") + ".mp4"

        # clean filename from unnecessary characters
        filename = "".join(x for x in filename if x.isalnum() or x in [" ", "-", "_", "."])

        recorded_filename = os.path.join(self._recorded_path, filename)

        subprocess.call(
            ["streamlink", "--twitch-oauth-token", self._access_token, "twitch.tv/" + self._channel,
             self._quality, "-o", recorded_filename])

        logging.info("recording stream is done, processing video file")
        return recorded_filename, filename








