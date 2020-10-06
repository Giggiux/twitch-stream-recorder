# Giggiux's Twitch Stream Recorder
This script allows you to record multiple twitch streams live to .mp4 files.
The idea started as an improved version of [ancalentari/twitch-stream-recorder](https://github.com/ancalentari/twitch-stream-recorder), which itself is an improved version of [junian's twitch-recorder](https://gist.github.com/junian/b41dd8e544bf0e3980c971b0d015f5f6), migrated to [**helix**](https://dev.twitch.tv/docs/api) - the new twitch API. It uses OAuth2.
This version allows  with channel recording, and possibility to add channels via a very simple **and insecure** http api.  
## Requirements
1. [python3.8](https://www.python.org/downloads/release/python-380/) or higher  
2. [streamlink](https://streamlink.github.io/)  
3. [ffmpeg](https://ffmpeg.org/)

## Setting up
1) If your version of streamlink is older than 1.4.1:
    * install new one and check the result with: `streamlink --version-check`

2) Install `requirements.txt` modules
   * Windows:    ```python -m pip install -r requirements.txt```  
   * Linux:      ```python3.8 -m pip install -r requirements.txt```
3) Create `config.py` file in the same directory as `twitch-recorder.py` with:
```properties
root_path = "/home/abathur/Videos/twitch"
recorded_path = "/home/abathur/Videos/twitch"
username = "defaultUsernameThatIsDefinitelyGoingToBeReplaced"
client_id = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
client_secret = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
password = "yourVerySecurePassword"
```
4) Create `channels.txt` file in the same directory as `twitch-recorder.py` with your channels username (one per line):
```properties
Ninja
TFue

```

## Running script
The server will be run as a insecure Flask server. If you want security, [check Flask deployment options](https://flask.palletsprojects.com/en/1.1.x/deploying/)

### On linux
Run the script
```shell script
FLASK_APP=main_api.py flask run
```
If you want to run the script as a job in the background and be able to close the terminal:
```shell script
FLASK_APP=main_api.py nohup flask run >/dev/null 2>&1 &
```
In order to kill the job, you first list them all:
```shell script
jobs
```
The output should show something like this:
```shell script
[1]+  Running                 nohup python3.8 twitch-recorder > /dev/null 2>&1 &
```
And now you can just kill the job:
```shell script
kill %1
```
