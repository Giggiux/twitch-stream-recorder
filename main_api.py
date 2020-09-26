from flask import Flask, abort
from markupsafe import escape
from twitch_recorder import TwitchRecorder
from multiprocessing import Process
import config
import time
app = Flask(__name__)

twitch_recorders = []
processes = []
channelsFile = 'channels.txt'


def run_all():
    # read all channels in text file
    with open(channelsFile) as f:
        content = f.readlines()

    # you may also want to remove whitespace characters like `\n` at the end of each line
    channels = [x.strip() for x in content]

    # get usernames of already created TwitchRecorder instances
    channels_ready = map(lambda tr: tr.username, twitch_recorders)
    # filter already created TwitchRecored instances' username
    new_channels = [channel for channel in channels if channel not in channels_ready]

    # create new TwitchRecorder instances for new channels
    for new_channel in new_channels:
        twitch_recorder = TwitchRecorder()
        twitch_recorder.username = new_channel

        twitch_recorders.append(twitch_recorder)

    # start all Twitch_Recorders
    for tr in twitch_recorders:
        if not tr.isRecording:
            p1 = Process(target=tr.run)
            p1.start()


def restart():
    print("Restart started")
    for tr in twitch_recorders:
        if not tr.isRecording:
            print(f"Stopping {tr.username}")
            tr.stop = True

    # Wait for one loop to end all recorders
    time.sleep(61)

    run_all()


def write_username_to_file(username):
    with open(channelsFile, "r+") as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        channels = [x.strip() for x in content]
        if username not in channels:
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
        restart()
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
        restart()
    else:
        abort(401)

    return 'Ok!'