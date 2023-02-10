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

# Start the app
if __name__ == "__main__":
    # handler.start()
    # slack_utils.send_message("Witajcie w Asgardzie!", [
    #                          "@kacper.iwi"], app.client)

    slack_utils.send_ephemeral_message(
        "Witajcie w Asgardzie!", "#asgard", "U03AECYM5MZ", app.client)

    slack_utils.send_scheduled_message(
        "Witajcie w Asgardzie!", "#asgard", datetime.datetime.combine(datetime.date.today(), datetime.time(hour=21, minute=31)), app.client)
