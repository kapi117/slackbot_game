"""
    This module contains the functions that are used to interact with the Slack API.

    Functions:
        - send_message: Sends a message to a Slack channel.
        - send_ephemeral_message: Sends an ephemeral message (disappearing one) to a Slack user.
        - send_scheduled_message: Sends a scheduled message to a Slack channel.
        - get_channel_users: Gets the users in a channel.
        - send_message_to_everyone_in_channel: Sends a message to everyone in a channel.
        - schedule_message_to_everyone_in_channel: Schedules a message to everyone in a channel.
        - get_parent_message: Gets the parent message of a thread.
"""

from slack_sdk.web.client import WebClient
from typing import List, Optional
import datetime


def send_message(message: str, channels: List[str], client: WebClient, thread_ts: Optional[List[str]] = None):
    """
        Sends a message to a Slack channels.

        Parameters:
            - message: The message to send.
            - channels: The channels or users to send the message to.
            - thread_ts: The threads to send the message to (can be given ts - then replies in thread to not thread message).

        Example:
            send_message("Hello!", ["#general", "@kacper"], app.client)
    """
    if thread_ts is None or len(thread_ts) != len(channels):
        thread_ts = [None]*len(channels)
    for channel, thread in zip(channels, thread_ts):
        client.chat_postMessage(
            channel=channel, text=message, thread_ts=thread)


def send_ephemeral_message(message: str, channel: str, user: str, client: WebClient, thread_ts: Optional[str] = None):
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
    return client.chat_postEphemeral(
        channel=channel, text=message, user=user, thread_ts=thread_ts)


def send_scheduled_message(message: str, channel: str, time: datetime.datetime, client: WebClient, thread_ts: Optional[str] = None):
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
    return client.chat_scheduleMessage(
        channel=channel, text=message, post_at=time.timestamp(), thread_ts=thread_ts)


def get_channel_users(channel: str, client: WebClient) -> List[str]:
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
    messages = []
    for user in users:
        messages.append(send_scheduled_message(message, user, time, client))
    return messages


def get_parent_message(channel: str, ts: str, client: WebClient) -> str:
    """
        Gets the parent message of a thread.

        Parameters:
            - channel: The channel the message is in.
            - ts: The timestamp of the message.

        Returns:
            - The parent message.

        Example:
            get_parent_message("C04P6595G5S", "1624941795.000200", app.client)
    """
    payload = client.conversations_replies(channel=channel, ts=ts)
    return payload['messages'][0]


def get_user_name(user_id: str, client: WebClient) -> str:
    """
        Gets the name of a user.

        Parameters:
            - user_id: The ID of the user.

        Returns:
            - The name of the user.

        Example:
            get_user_name("U123123123", app.client)
    """
    payload = client.users_info(user=user_id)
    return payload['user']['name']


def update_message(channel: str, ts: str, message: str, client: WebClient):
    """
        Updates a message.

        Parameters:
            - channel: The channel the message is in.
            - ts: The timestamp of the message.
            - message: The new message.

        Example:
            update_message("C04P6595G5S", "1624941795.000200", "Hello!", app.client)
    """
    return client.chat_update(channel=channel, ts=ts, text=message)


def delete_message(channel: str, ts: str, client: WebClient):
    """
        Deletes a message.

        Parameters:
            - channel: The channel the message is in.
            - ts: The timestamp of the message.

        Example:
            delete_message("C04P6595G5S", "1624941795.000200", app.client)
    """
    return client.chat_delete(channel=channel, ts=ts)
