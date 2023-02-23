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
ADMIN_USER_ID = "U03AECYM5MZ"

# Events


@app.event("message")
def message_im(payload, say, client):
    """
        Handles a direct message to the bot.
    """
    print("[MSG] Received message")
    # Get the message
    message = payload["text"]

    # Get the user that sent the message
    user = payload["user"]

    # Get the channel
    channel = payload["channel"]

    thread_ts = payload["ts"]
    if "thread_ts" in payload:
        thread_ts = payload["thread_ts"]

    # Check if the message is a DM
    if channel[0] == "D":
        print("[MSG] Direct message {}, {}, {}, {}, {}".format(
            "Hey <@"+user+">", user, user, client, thread_ts))
        # Send the message
        mess = slack_utils.send_ephemeral_message(
            "Hey <@"+user+">", user, user, client, thread_ts=thread_ts)
        print(f"[MSG] Sent message {mess}")
        try:
            words = message.split(" ")
            if user == ADMIN_USER_ID and words[0].lower() == "odin":
                # Handle too few words
                if len(words) == 1:
                    slack_utils.send_message(
                        "To check available commands type `odin help`",
                        [channel], client, thread_ts=[thread_ts])
                    return

                # Available admin commands
                ADMIN_COMMANDS = ["help", "write_on_channel",
                                  "write_to_everyone", "show_players"]
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
        except Exception as e:
            slack_utils.send_ephemeral_message(
                "There was an error :(", channel, user, client, thread_ts=thread_ts)
            print(e)


@app.event("member_joined_channel")
def member_joined_channel(payload, say, client):
    """
        Handles a new user joining the channel.
    """
    # Get the user
    user = payload["user"]

    # Get the channel
    channel = payload["channel"]

    # Check if the user joined the channel
    if channel == ASGARD_CHANNEL:
        # Send the message
        message = "Przekroczyłeś Bifrost, witamy w Asgardzie <@"+user+">!"
        # slack_utils.send_ephemeral_message(
        #     message, channel, user, client)
        client.chat_postEphemeral(
            channel=channel, text=message, user=user, username="Hajmdal", icon_url="https://static.wikia.nocookie.net/m__/images/a/a5/Heimdall.PNG/revision/latest?cb=20200924165806&path-prefix=marvel%2Fpl")
        # TODO Add user to the database


# Start the app
if __name__ == "__main__":
    handler.start()

    pass
