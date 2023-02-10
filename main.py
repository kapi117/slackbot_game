"""
    Author:     Kacper Iwicki
    Created:    2023-02-10
    Edited:     2023-02-10
    Desc:       Main file for the project
    Mail:       kacper.iwi@gmail.com
"""

# Imports
from dotenv import load_dotenv
import os
from pathlib import Path
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import slack_utils
import datetime

# Load .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize app
app = App(token=os.environ.get("BOT_TOKEN"))

# Socket mode handler
handler = SocketModeHandler(app, os.environ.get("APP_TOKEN"))

# Constants
ASGARD_CHANNEL = "C04P6595G5S"

# Events


@app.event("message")
def message_im(payload, say, client):
    """
        Handles a direct message to the bot.
    """
    # Get the message
    message = payload["text"]

    # Get the user that sent the message
    user = payload["user"]

    # Get the channel
    channel = payload["channel"]

    thread_ts = None
    if "thread_ts" in payload:
        thread_ts = payload["thread_ts"]

    # Check if the message is a DM
    if channel[0] == "D":
        # Send the message
        slack_utils.send_ephemeral_message(
            "Hey <@"+user+">", channel, user, client, thread_ts=thread_ts)


# Start the app
if __name__ == "__main__":
    handler.start()

    pass
