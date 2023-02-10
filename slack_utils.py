"""
    This module contains the functions that are used to interact with the Slack API.

    Functions:
        - send_message: Sends a message to a Slack channel.
        - send_ephemeral_message: Sends an ephemeral message (disappearing one) to a Slack user.
        - send_scheduled_message: Sends a scheduled message to a Slack channel.
        - get_channel_users: Gets the users in a channel.
        - send_message_to_everyone_in_channel: Sends a message to everyone in a channel.
"""

from slack_sdk import WebClient
from typing import List
import datetime


def send_message(message: str, channels: List[str], client: WebClient, thread_ts: List[str] = None):
    """
        Sends a message to a Slack channels.

        Parameters:
            - message: The message to send.
            - channels: The channels or users to send the message to.
            - thread_ts: The threads to send the message to.

        Example:
            send_message("Hello!", ["#general", "@kacper"], app.client)
    """
    if thread_ts is None or len(thread_ts) != len(channels):
        thread_ts = [None]*len(channels)
    for channel, thread in zip(channels, thread_ts):
        client.chat_postMessage(
            channel=channel, text=message, thread_ts=thread)


def send_ephemeral_message(message: str, channel: str, user: str, client: WebClient, thread_ts: str = None):
    """
        Sends an ephemeral message to a Slack user.

        Parameters:
            - message: The message to send.
            - channel: The channel to send the message to.
            - user: The user to send the message to.
            - thread_ts: The thread to send the message to.

        Example:
            send_ephemeral_message("Hello!", "#general", "U12312311", app.client)
    """
    client.chat_postEphemeral(
        channel=channel, text=message, user=user, thread_ts=thread_ts)


def send_scheduled_message(message: str, channel: str, time: datetime, client: WebClient, thread_ts: str = None):
    """
        Sends a scheduled message to a Slack channel.

        Parameters:
            - message: The message to send.
            - channel: The channel to send the message to.
            - time: The time to send the message at.
            - thread_ts: The thread to send the message to.

        Example:
            send_scheduled_message("Hello!", "#general", datetime.datetime.combine(datetime.date.today(), datetime.time(hour=21, minute=31)), app.client)
    """
    client.chat_scheduleMessage(
        channel=channel, text=message, post_at=time.timestamp(), thread_ts=thread_ts)


def get_channel_users(channel: str, client: WebClient):
    """
        Gets the users in a channel.

        Parameters:
            - channel: The channel to get the users from.

        Returns:
            - A list of the users in the channel.

        Example:
            get_channel_users("C04P6595G5S", app.client)
    """
    payload = client.conversations_members(channel=channel)
    return payload['members']


def send_message_to_everyone_in_channel(message: str, channel: str, client: WebClient):
    """
        Sends a message to everyone in a channel.

        Parameters:
            - message: The message to send.
            - channel: The channel to send the message to.

        Example:
            send_message_to_everyone_in_channel("Hello!", "C04P6595G5S", app.client)
    """
    users = get_channel_users(channel, client)
    send_message(message, users, client)


def schedule_message_to_everyone_in_channel(message: str, channel: str, time: datetime, client: WebClient):
    """
        Sends a message to everyone in a channel.

        Parameters:
            - message: The message to send.
            - channel: The channel to send the message to.
            - time: The time to send the message at.

        Example:
            send_message_to_everyone_in_channel("Hello!", "C04P6595G5S", datetime.datetime.combine(datetime.date.today(), datetime.time(hour=21, minute=31)), app.client)
    """
    users = get_channel_users(channel, client)
    for user in users:
        send_scheduled_message(message, user, time, client)
