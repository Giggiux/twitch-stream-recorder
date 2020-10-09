from flask import Flask, abort
from markupsafe import escape
from actors.twitch_coordinator import TwitchCoordinator
import config
import logging
import time
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
channelsFile = 'channels.txt'

coordinator = TwitchCoordinator.start().proxy()


def run_all():
    # read all channels in text file
    with open(channelsFile) as f:
        content = f.readlines()

    # you may also want to remove whitespace characters like `\n` at the end of each line
    channels = [x.strip() for x in content]

    for channel in channels:
        print("adding channel:", channel)
        coordinator.add_channel(channel)


def restart():
    print("Restart started")
    coordinator.stop_all()
    coordinator.start_all()


def write_username_to_file(username):
    with open(channelsFile, "r+") as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        channels = [x.strip() for x in content]
        if username not in channels and len(username) >= 3:
            f.write(f"{username}\n")


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/api/<password>/add/<username>')
def api_add_username(password, username):
    username = escape(username)
    password = escape(password)

    if password == config.password:
        print(username, "added")
        write_username_to_file(username)
        coordinator.add_channel(username)
    else:
        abort(401)

    return 'Ok!'


@app.route('/api/<password>/run')
def api_run(password):
    print("Received run request")
    password = escape(password)

    if password == config.password:
        print("Password accepted")
        run_all()
    else:
        abort(401)

    return 'Ok!'


@app.route('/api/<password>/restart')
def api_restart(password):
    print("Received run request")
    password = escape(password)

    if password == config.password:
        print("Password accepted")
        coordinator.restart_all()
    else:
        abort(401)

    return 'Ok!'