"""
    This module containts the Player class, which is used to store the information about the users in the game.
"""
from typing import Dict, Set, List, Optional
from datetime import datetime

import slack
import slack_utils

'''
@startuml
class Task {
  +task_no: int
  +points: int
  +correct_answers: List[str]
  +needed_task: int
  +is_dm: bool
  +channel: str
  +date_and_time: datetime
  +description: str
  +do_letters_case_matter: bool
  +solved_by: int = 0
  +sent_messages: List[int]


  + {static} create_task_from_modal() : Task
  +__init__(task_no: int, points: int, correct_answers: List[str], needed_task: Optional[int] = None, is_dm: bool = False, channel: str = None, date_and_time: datetime = None, description: str = None, do_letters_case_matter: bool = False)
  +schedule_task()
  +send_task(user_id: str)
  +edit_task(**kwargs)
  +update_message()
  +delete_message()
  +__str__() : str
  +check_answer(message: str) : bool
}

class Player {
  +user_id: str
  +points: int = 0
  +completed_tasks: Set[int]
  +standings: Dict[int, int]
  +wrong_answers: Dict[int, int]
  
  +__init__(user_id: str)
  +right_answer(task_no: int)
  +wrong_answer(task_no: int)
  
}

enum MessageType {
  +RIGHT_ANSWER
  +WRONG_ANSWER
  +OUTER_MESSAGE
  +ADMIN_MESSAGE
}

class Game {
  +players: Dict[str, Player]
  +tasks: Dict[int, Task]
  +needed_tasks: Dict[int, int]
  +{static} QUOTES: List[str]
  +{static} INCORRECT_REPLIES: List[str]
  +{static} CORRECT_REPLIES: List[str]

  +add_task(task_no: int, points: int, correct_answer: str, needed_task: int)
  +edit_task(task_no: int, **kwargs)
  +delete_task(task_no: int)
  +show_tasks() : str
  +add_player(user_id: str)
  +show_players() : str
  +handle_message(message: str, parent_message: str) : MessageType

  +{static} save_to_pickle(game: Game, filename: str)
  +{static} load_from_pickle(filename: str) : Game
}
@enduml
'''


class Task:
    """
        This class is used to store the information about the tasks in the game.

        Attributes:
            - task_no: The number of the task.
            - points: The number of points the task is worth.
            - description: The description of the task.
            - correct_answers: The correct answers to the task.
            - do_letters_case_matter: Whether the letters case matters or not.
            - needed_task: The number of the task that is needed to be completed before this task can be completed.
            - is_dm: Whether the task is a DM task or not.
            - channel: The channel the task is in (if not dm).
            - date_and_time: The date and time the task is scheduled for.
            - solved_by: The number of users that have solved the task.
            - sent_messages: The IDs of the messages that have been sent to the users.

        Methods:
            - create_task_from_modal: Creates a task from the modal.
            - __init__: The constructor.
            - schedule_task: Schedules the task.
            - send_task: Sends the task to the users.
            - edit_task: Edits the task.
            - update_message: Updates the message.
            - delete_message: Deletes the message.
            - __str__: Returns the string representation of the task.
            - check_answer: Checks if the answer is correct.
    """

    def __init__(self, task_no: int, points: int, correct_answers: List[str], needed_task: Optional[int] = None, is_dm: bool = False, channel: str = None, date_and_time: datetime = None, description: str = None, do_letters_case_matter: bool = False):
        """
            The constructor.

            Parameters:
                - task_no: The number of the task.
                - points: The number of points the task is worth.
                - correct_answers: The correct answers to the task.
                - needed_task: The number of the task that is needed to be completed before this task can be completed.
                - is_dm: Whether the task is a DM task or not.
                - channel: The channel the task is in (if not dm).
                - date_and_time: The date and time the task is scheduled for.
                - description: The description of the task.
                - do_letters_case_matter: Whether the letters case matters or not.
        """
        self.task_no = task_no
        self.points = points
        self.correct_answers = correct_answers
        self.needed_task = needed_task
        self.is_dm = is_dm
        self.channel = channel
        self.date_and_time = date_and_time
        self.description = description
        self.do_letters_case_matter = do_letters_case_matter
        self.solved_by = 0
        self.sent_messages = []

    @staticmethod
    def create_task_from_modal() -> 'Task':
        """
            Creates a task from the modal.

            Returns:
                The task.
        """
        pass

    def update_message(self, client: slack.WebClient):
        """
            Updates the message.

            Parameters:
                - client: The slack client.
        """
        for message in self.sent_messages:
            slack_utils.update_message(message, self.description, client)

    def delete_message(self, client: slack.WebClient):
        """
            Deletes the message.

            Parameters:
                - client: The slack client.
        """
        for message in self.sent_messages:
            slack_utils.delete_message(message, client)

    def schedule_task(self, client: slack.WebClient):
        """
            Schedules the task.
        """
        if len(self.sent_messages) > 0:
            # TODO delete scheduled messages
            pass

        if not self.is_dm:
            mess = slack_utils.send_scheduled_message(self.description,
                                                      self.channel, self.date_and_time, client)
            self.sent_messages.append(mess)
        else:
            messages = slack_utils.schedule_message_to_everyone_in_channel(self.description,
                                                                           self.channel, self.date_and_time, client)
            self.sent_messages = messages

    def send_task(self, user_id: str, client: slack.WebClient):
        """
            Sends the task to the users.

            Parameters:
                - user_id: The user ID of the user.
        """
        if len(self.sent_messages) < 1:
            mess = slack_utils.send_message(
                self.description, [user_id], client)
            self.sent_messages.append(mess)

    def edit_task(self, client, **kwargs):
        """
            Edits the task.

            Parameters:
                - **kwargs: The arguments to edit.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        if self.needed_task is None:
            self.schedule_task(client)

    def check_answer(self, answer: str) -> bool:
        """
            Checks if the answer is correct.

            Parameters:
                - answer: The answer to check.

            Returns:
                True if the answer is correct, False otherwise.
        """
        if self.do_letters_case_matter:
            return answer in self.correct_answers
        else:
            return answer.lower() in [x.lower() for x in self.correct_answers]

    def __str__(self) -> str:
        """
            Returns the string representation of the task.

            Returns:
                The string representation of the task.
        """
        return f"Task {self.task_no} - {self.points} points - {self.description}"


class Player:
    """
        This class is used to store the information about the users in the game.

        Attributes:
            - user_id: The user ID of the user.
            - points: The number of points the user has.
            - completed_tasks: The number of tasks the user has completed.

    """
