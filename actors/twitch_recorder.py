import enum
import datetime
import logging
import os
import shutil
import time
import pykka
import requests

import config

from actors.streamlink import Streamlink
from actors.ffmpeg import Ffmpeg


class TwitchResponseStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4


class TwitchRecorder(pykka.ThreadingActor):
    def __init__(self, channel: str, access_token: str, client_id: str,  coordinator):
        super().__init__()
        logging.debug("Twitch recorded init starts")
        self._in_future = self.actor_ref.proxy()

        self._channel: str = channel
        self._access_token: str = access_token
        self._coordinator = coordinator
        self._client_id: str = client_id

        logging.info("Creating ffmpeg for channel: %s", channel)
        self._ffmpeg = Ffmpeg.start(channel).proxy()
        logging.info("Creating streamlink for channel: %s", channel)
        self._streamlink = Streamlink.start(channel, access_token, client_id).proxy()

        # Time between a request and another
        self._refresh = 60

        self._url = "https://api.twitch.tv/helix/streams"
        logging.info("Created Twitch Recorder for channel: %s", channel)

    def _check_user(self):
        info = None
        status = TwitchResponseStatus.ERROR
        try:
            headers = {"Client-ID": self._client_id, "Authorization": "Bearer " + self._access_token}
            r = requests.get(self._url + "?user_login=" + self._channel, headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
        return status, info

    def start_record(self):
        logging.info("Checking if channel is online: %s", self._channel)
        self._ffmpeg.fix_all().get()
        status, info = self._check_user()
        if status == TwitchResponseStatus.NOT_FOUND:
            logging.error("username not found, invalid username or typo")
            time.sleep(self._refresh)
        elif status == TwitchResponseStatus.ERROR:
            logging.error("%s unexpected error. will try again in 5 minutes",
                          datetime.datetime.now().strftime("%Hh%Mm%Ss"))
            time.sleep(300)
        elif status == TwitchResponseStatus.OFFLINE:
            logging.info("%s currently offline, checking again in %s seconds", self._channel, self._refresh)
            time.sleep(self._refresh)
        elif status == TwitchResponseStatus.UNAUTHORIZED:
            logging.info("unauthorized, will attempt to log back in immediately")
            self._access_token = self._coordinator.get_auth_code().get()
        elif status == TwitchResponseStatus.ONLINE:
            recorded_filename, filename = self._streamlink.record(info).get()
            self._ffmpeg.fix(recorded_filename, filename, True).get()
            time.sleep(self._refresh)

        self._in_future.start_record()









