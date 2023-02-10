"""
    This module contains the functions that are used to interact with the Slack API.

    Functions:
        - send_message: Sends a message to a Slack channel.
        - send_ephemeral_message: Sends an ephemeral message (disappearing one) to a Slack user.
"""

from slack_sdk import WebClient
from typing import List
import datetime


def send_message(message: str, channels: List[str], client: WebClient):
    """
        Sends a message to a Slack channels.

        Parameters:
            - message: The message to send.
            - channels: The channels or users to send the message to.

        Example:
            send_message("Hello!", ["#general", "@kacper"], app.client)
    """
    for channel in channels:
        client.chat_postMessage(channel=channel, text=message)


def send_ephemeral_message(message: str, channel: str, user: str, client: WebClient):
    """
        Sends an ephemeral message to a Slack user.

        Parameters:
            - message: The message to send.
            - channel: The channel to send the message to.
            - user: The user to send the message to.

        Example:
            send_ephemeral_message("Hello!", "#general", "U12312311", app.client)
    """
    client.chat_postEphemeral(channel=channel, text=message, user=user)


def send_scheduled_message(message: str, channel: str, time: datetime, client: WebClient):
    """
        Sends a scheduled message to a Slack channel.

        Parameters:
            - message: The message to send.
            - channel: The channel to send the message to.
            - time: The time to send the message at.

        Example:
            send_scheduled_message("Hello!", "#general", datetime.datetime.combine(datetime.date.today(), datetime.time(hour=21, minute=31)), app.client)
    """
    payload = client.chat_scheduleMessage(
        channel=channel, text=message, post_at=time.timestamp())
    print(payload)
