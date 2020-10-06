import pykka
import requests
import logging
from typing import List

import config

from actors.twitch_recorder import TwitchRecorder


class TwitchCoordinator(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()
        self._in_future = self.actor_ref.proxy()

        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self._token_url = "https://id.twitch.tv/oauth2/token?client_id=" + self._client_id + "&client_secret=" \
                          + self._client_secret + "&grant_type=client_credentials"

        self._channels: List[str] = []
        self._dictChannel = {}
        self._access_token = ""
        logging.info("Starting Coordinator")

    def add_channel(self, channel: str):
        if channel and channel not in self._channels:
            logging.info("Adding Channel: %s", channel)
            self._channels.append(channel)
            self._in_future.start_channel(channel)
        return True

    def start_channel(self, channel):
        logging.info("Starting channel: %s", channel)
        if not self._access_token:
            logging.info("No token found")
            self.get_auth_code()

        if channel not in self._dictChannel:
            logging.debug("Creating TwitchRecorder instance for %s", channel)
            self._dictChannel[channel] = TwitchRecorder.start(channel, self._access_token, self._client_id, self._in_future).proxy()
            logging.debug("Created TwitchRecorder instance for %s", channel)

        self._dictChannel[channel].start_record()
        logging.debug("dict: %s", self._dictChannel)

    def get_auth_code(self):
        logging.info("Getting token")
        token_response = requests.post(self._token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()

        self._access_token = token["access_token"]
        logging.info("Returning token")
        return self._access_token

    def stop_channel(self, channel):
        actor = self._dictChannel[channel]
        if actor:
            actor.stop()

    def stop_all(self):
        for channel in self._channels:
            self._in_future.stop_channel(channel)

    def start_all(self):
        for channel in self._channels:
            self._in_future.start_channel(channel)

    def restart_all(self):
        self._in_future.stop_all()
        self._in_future.start_all()




