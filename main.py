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
import game_utils
import datetime
import logging

# Load .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize app
app = App(token=os.environ.get("BOT_TOKEN"))

# Socket mode handler
handler = SocketModeHandler(app, os.environ.get("APP_TOKEN"))

# Constants
ASGARD_CHANNEL = "C04P6595G5S"
ADMIN_USER_IDS = ["U03AECYM5MZ"]

# Logging
LOG_FILE = "logs/logs.log"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, encoding="utf-8",
                    format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

# Game
GAME_FILE = "saved/game_save"
game = game_utils.Game.load_from_pickle(GAME_FILE)

# App home
with open("modals/app_home.txt", "r", encoding="utf-8") as f:
    APP_HOME_VIEW = f.read()

# Modals
ADD_TASK_ID = "add_task_modal"
with open("modals/add_task.txt", "r", encoding="utf-8") as f:
    ADD_TASK_VIEW = f.read()

SEND_MESSAGE_ID = "send_message_modal"
with open("modals/send_message.txt", "r", encoding="utf-8") as f:
    SEND_MESSAGE_VIEW = f.read()

# IDs in modals
BLOCK_CHANNEL_ID = "channel_to_send"
SELECTED_CHANNEL_ID = "select_channel"

BLOCK_DATE_ID = "date_planned"
SELECTED_DATE_ID = "select_date"

BLOCK_MESSAGE_ID = "message_to_send"
SELECTED_MESSAGE_ID = "select_message"


def open_modal(modal_id, trigger_id, client):
    """
        Opens a modal with a given id
    """
    if modal_id == ADD_TASK_ID:
        client.views_open(
            trigger_id=trigger_id,
            view=ADD_TASK_VIEW
        )
    elif modal_id == SEND_MESSAGE_ID:
        client.views_open(
            trigger_id=trigger_id,
            view=SEND_MESSAGE_VIEW
        )

# Events


@app.action("app_home_buttons")
def app_home_buttons(client, ack, body, action):
    trigger_id = body["trigger_id"]
    ack()
    open_modal(action["value"], trigger_id, client)


@app.event("app_home_opened")
def app_home_opened(client, event):
    if event["user"] in ADMIN_USER_IDS:
        client.views_publish(
            user_id=event["user"],
            view=APP_HOME_VIEW
        )
    else:
        client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": " *You are not an admin* "
                        }
                    }
                ]
            }
        )


@app.event("message")
def message_im(payload, say, client):
    """
        Handles a direct message to the bot.
    """
    print(payload)
    logging.debug("[MSG] Received message")
    # Get the message
    message = payload["text"]

    # Get the user that sent the message
    user = payload["user"]

    # Get the channel
    channel = payload["channel"]

    thread_ts = payload["ts"]

    is_thread = False
    if "thread_ts" in payload:
        thread_ts = payload["thread_ts"]
        is_thread = True

    logging.debug("[MSG] Message: {}, user: {}, channel: {}, thread_ts: {}, is_thread: {}".format(
        message, user, channel, thread_ts, is_thread))

    # Check if the message is a DM
    if channel[0] == "D":
        logging.debug("[MSG] Message is a DM")
        try:
            words = message.split(" ")
            if user in ADMIN_USER_IDS and words[0].lower() == "odin":
                # Handle too few words
                if len(words) == 1:
                    slack_utils.send_message(
                        "To check available commands type `odin help`",
                        [channel], client, thread_ts=[thread_ts])
                    return

                # Available admin commands
                ADMIN_COMMANDS = ["help", "write_on_channel",
                                  "write_to_everyone", "show_players", "add_task"]
                # Non-existent command
                if words[1] not in ADMIN_COMMANDS:
                    slack_utils.send_ephemeral_message(
                        "There is no command '" +
                        words[1]+"', to check available commands type `odin help",
                        channel, user, client, thread_ts=thread_ts)
                else:
                    if words[1] == "help":
                        # Show available commands
                        slack_utils.send_message(
                            "Available commands are: " + str(ADMIN_COMMANDS),
                            [channel], client, [thread_ts]
                        )
                    elif words[1] == "write_on_channel":
                        if len(words) < 6:
                            slack_utils.send_ephemeral_message(
                                "Usage: odin " + words[1] + " [date YYYY/MM/DD] [time HH:MM] [#channel] MESSAGE: [text]\n" +
                                "Example: odin " +
                                words[1] +
                                " 2023/02/28 21:37 asgard MESSAGE: papieżowa",
                                channel, user, client, thread_ts=thread_ts)
                            return
                        try:
                            d = datetime.datetime.strptime(
                                words[2], "%Y/%m/%d")
                            t = datetime.datetime.strptime(words[3], "%H:%M")
                        except ValueError:
                            slack_utils.send_ephemeral_message(
                                "Wrong date or time format\n" +
                                "Usage: odin " + words[1] + " [date YYYY/MM/DD] [time HH:MM] [#channel] MESSAGE: [text]\n" +
                                "Example: odin " +
                                words[1] +
                                " 2023/02/28 21:37 asgard MESSAGE: papieżowa",
                                channel, user, client, thread_ts=thread_ts)
                            return
                        channel = words[4]
                        print(str(channel), type(channel))
                        message = " ".join(words[6:])
                        slack_utils.send_scheduled_message(
                            message, channel, datetime.datetime.combine(
                                d.date(), t.time()), client
                        )

                    elif words[1] == "write_to_everyone":
                        if len(words) < 6:
                            slack_utils.send_ephemeral_message(
                                "Usage: odin " + words[1] + " [date YYYY/MM/DD] [time HH:MM] [#channel_to_get_people_from] MESSAGE: [text]\n" +
                                "Example: odin " +
                                words[1] +
                                " 2023/02/28 21:37 asgard MESSAGE: papieżowa",
                                channel, user, client, thread_ts=thread_ts)
                            return
                        try:
                            d = datetime.datetime.strptime(
                                words[2], "%Y/%m/%d")
                            t = datetime.datetime.strptime(words[3], "%H:%M")
                        except ValueError:
                            slack_utils.send_ephemeral_message(
                                "Wrong date or time format\n" +
                                "Usage: odin " + words[1] + " [date YYYY/MM/DD] [time HH:MM] [#channel] MESSAGE: [text]\n" +
                                "Example: odin " +
                                words[1] +
                                " 2023/02/28 21:37 asgard MESSAGE: papieżowa",
                                channel, user, client, thread_ts=thread_ts)
                            return
                        channel = words[4]
                        message = " ".join(words[6:])
                        for user in slack_utils.get_channel_users(channel, client):
                            slack_utils.send_scheduled_message(
                                message, user, datetime.datetime.combine(
                                    d.date(), t.time()), client
                            )
                        pass
                    elif words[1] == "show_players":
                        # TODO show players and points
                        pass
                    elif words[1] == "add_task":
                        open_modal(ADD_TASK_ID, trigger_id, client)
        except Exception as e:
            slack_utils.send_ephemeral_message(
                "There was an error :(", channel, user, client, thread_ts=thread_ts)
            print(e)


@app.event("member_joined_channel")
def member_joined_channel(payload, say, client):
    """
        Handles a new user joining the channel, adding him to the game
    """
    # Get the user
    user = payload["user"]

    # Get the channel
    channel = payload["channel"]

    # Check if the user joined the channel
    if channel == ASGARD_CHANNEL:
        # Send the message
        message = "Przekroczyłeś Bifrost, witamy w Asgardzie <@"+user+">!"
        client.chat_postEphemeral(
            channel=channel, text=message, user=user, username="Hajmdal", icon_url="https://static.wikia.nocookie.net/m__/images/a/a5/Heimdall.PNG/revision/latest?cb=20200924165806&path-prefix=marvel%2Fpl")
        game.add_player(user)
        game.save_to_pickle(GAME_FILE)


@app.view(SEND_MESSAGE_ID)
def send_message_submission(body, client, ack):
    """
        Handles the submission of the send message modal
    """
    # Acknowledge the request
    ack()
    logging.debug("[SEND_MSG] Received submission: " + str(body))

    # Get the user
    user = body["user"]["id"]

    # Get the channel
    channels = body["view"]["state"]["values"][BLOCK_CHANNEL_ID][SELECTED_CHANNEL_ID]["selected_conversations"]

    # Get the date
    date = body["view"]["state"]["values"][BLOCK_DATE_ID][SELECTED_DATE_ID]["selected_date_time"]

    # Get the message
    message = body["view"]["state"]["values"][BLOCK_MESSAGE_ID][SELECTED_MESSAGE_ID]["value"]

    # Send the message
    for channel in channels:
        mess = slack_utils.send_scheduled_message(
            message, channel, datetime.datetime.fromtimestamp(date), client)
        logging.debug("[SEND_MSG] Scheduled message: " + message +
                      " to " + channel + " at " + str(date))
        logging.debug("[SEND_MSG] Message data: " + str(mess))


# Start the app
if __name__ == "__main__":
    handler.start()
