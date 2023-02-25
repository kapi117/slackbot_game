"""
    This module containts the Player class, which is used to store the information about the users in the game.
"""
from enum import Enum
import os
import pickle
import random
from typing import Any, Dict, Set, List, Optional
from datetime import datetime

from slack_sdk.web.client import WebClient
import slack_utils
import logging


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

    def __init__(self, task_no: int, points: int, correct_answers: Optional[List[str]], needed_task: Optional[int] = None, is_dm: bool = False, channel: str = None, date_and_time: datetime = None, description: str = None, do_letters_case_matter: bool = False):
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
        # Add the task number and points to the description.
        self.description = f'[ZADANIE #{task_no} warte {points} punktów]\n' + description
        self.do_letters_case_matter = do_letters_case_matter
        self.solved_by = 0
        self.sent_messages = []
        logging.info(f"[TASK] Task {self.task_no} created.")

    @staticmethod
    def create_task_from_modal() -> 'Task':
        """
            Creates a task from the modal.

            Returns:
                The task.
        """

        pass

    def update_message(self, client: WebClient):
        """
            Updates the message.

            Parameters:
                - client: The slack client.
        """
        for message in self.sent_messages:
            slack_utils.update_message(message, self.description, client)

    def delete_message(self, client: WebClient):
        """
            Deletes the message.

            Parameters:
                - client: The slack client.
        """
        for message in self.sent_messages:
            slack_utils.delete_message(message, client)

    def schedule_task(self, client: WebClient, player_ids: List[str]):
        """
            Schedules the task.
        """
        if len(self.sent_messages) > 0:
            # TODO delete scheduled messages
            pass

        metadata_task = {"event_type": f"{self.task_no}",
                         "event_payload": {"task_no": f"{self.task_no}"}}
        if not self.is_dm:
            mess = slack_utils.send_scheduled_message(self.description,
                                                      self.channel, self.date_and_time, client, metadata=metadata_task)
            self.sent_messages.append(mess)
        else:
            messages = []
            for player_id in player_ids:
                messages.append(slack_utils.send_scheduled_message(self.description,
                                                                   player_id, self.date_and_time, client, metadata=metadata_task))
            self.sent_messages = messages
        logging.info(f"[TASK] Task {self.task_no} scheduled.")

    def send_task(self, user_id: str, client: WebClient):
        """
            Sends the task to the users.

            Parameters:
                - user_id: The user ID of the user.
        """
        metadata_task = {"event_type": f"{self.task_no}",
                         "event_payload": {"task_no": f"{self.task_no}"}}
        logging.info(f"[TASK] Sending task {self.task_no} to {user_id}.")
        mess = slack_utils.send_message(
            self.description, [user_id], client, metadata=metadata_task)
        self.sent_messages.append(mess)
        logging.info(f"[TASK] Task {self.task_no} sent to {user_id}.")

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
        logging.info(
            f"[TASK] Checking answer {answer} for task {self.task_no}.")
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
        return f" Task {self.task_no} \n {self.points} points \n Description: {self.description} \n Correct answers: {self.correct_answers} \n Needed task: {self.needed_task} \n Is DM: {self.is_dm} \n Channel: {self.channel} \n Date and time: {self.date_and_time} \n Solved by: {self.solved_by}"


class Player:
    """
        This class is used to store the information about the users in the game.

        Attributes:
            - user_id: The user ID of the user.
            - points: The number of points the user has.
            - completed_tasks: The number of tasks the user has completed.
            - standings: The standings of the user.
            - wrong_answers: The number of wrong answers the user has.
    """

    def __init__(self, user_id: str):
        """
            The constructor.

            Parameters:
                - user_id: The user ID of the user.
        """
        self.user_id = user_id
        self.points = 0
        self.completed_tasks = set()
        self.standings = {}
        self.wrong_answers = {}
        logging.info(f"[PLAYER] Player {self.user_id} created.")

    def right_answer(self, task: Task):
        """
            Updates the user's information after he/she answered correctly.

            Parameters:
                - task: The task.
        """
        if task.task_no not in self.completed_tasks:
            self.points += int(task.points)
            self.completed_tasks.add(task.task_no)
            task.solved_by += 1
            self.standings[task.task_no] = task.solved_by
            logging.info(
                f"[PLAYER] Player {self.user_id} answered correctly to task {task.task_no}.")

    def wrong_answer(self, task: Task):
        """
            Updates the user's information after he/she answered incorrectly.

            Parameters:
                - task: The task.
        """
        if task.task_no not in self.wrong_answers:
            self.wrong_answers[task.task_no] = 1
        else:
            self.wrong_answers[task.task_no] += 1
        logging.info(
            f"[PLAYER] Player {self.user_id} answered incorrectly to task {task.task_no}.")

    def __str__(self) -> str:
        """
            Returns the string representation of the player.

            Returns:
                The string representation of the player.
        """
        return f"{self.user_id} - {self.points} points - {self.completed_tasks} completed tasks - {self.wrong_answers} wrong answers - {self.standings} standings"


class MessageType(Enum):
    RIGHT_ANSWER = 1
    WRONG_ANSWER = 2
    OUTER_MESSAGE = 3
    ADMIN_MESSAGE = 4


class Game:
    """
        This class is used to store the information about the game.

        Attributes:
            - tasks: The tasks of the game.
            - players: The players of the game.
            - needed_task: Maps the task number that is needed to be completed before a task can be completed.
            - RANDOM_QUOTES: Random quotes to send to the users.
            - CORRECT_ANSWER_MESSAGES: Messages to send to the users when they answer correctly.
            - WRONG_ANSWER_MESSAGES: Messages to send to the users when they answer incorrectly.
    """

    RANDOM_QUOTES = ["Wiesz, że moja siostra Hel rządzi krainą zmarłych? To niezbyt przyjemne miejsce, ale czasem trzeba tam zajrzeć.",    "Powiedziano, że moje oko, które oddałem w ofierze, jest ukryte na dnie studni Mimir. Kto wie, co może zrobić z takim darem?",    "Czy wiesz, że kiedyś prawie pokonałem samego Hrymira w grze w hnefatafl? To była prawdziwa walka.",    "Mój ulubiony wojownik, Starkad, zabił swoją żonę, swojego ojca i swojego najlepszego przyjaciela. To dopiero był wojownik.",    "Każdego ranka wołami przed moim pałacem prowadzi Freyja, bogini miłości. Ale to tylko jedna z jej wielu ról.",
                     "Słyszałeś o wojowniku, który zabił smoka i zjadł jego serce? Tak, Fafnir to był kawał mężczyzny.",    "Gdy byłem młodym wojownikiem, kiedyś zabiłem giganta Ymira i z jego ciała stworzyliśmy świat.",    "Czy wiesz, że jeden z moich synów, Balder, był niemalże nieśmiertelny, ale zginął trafiony strzałą z jemioły? To była wielka strata.",    "Miałem niezwykłe doświadczenie, kiedy skradłem z drzewa wiedzy jeden z jabłek Idun, które dają wieczną młodość. To naprawdę działa!",    "Jeśli kiedykolwiek spotkasz wojownika zwanego berserkerem, uważaj, bo to są moi najlepsi wojownicy i są w stanie osiągnąć niemalże nieludzkie siły i zdolności bojowe."]

    CORRECT_ANSWER_MESSAGES = [
        "Twoja mądrość jest godna szacunku, człowieku.",
        "Wiesz więcej niż inni o mitologii nordyckiej, ludzie potrafią się od Ciebie wiele nauczyć.",
        "Właśnie tak, wiedza o bogach zasługuje na pochwałę, cieszę się, że jej nie brakuje u Ciebie.",
        "Czuję, że powinieneś zostać jednym z moich berserków, twoja mądrość nie ma sobie równych.",
        "Brawo, wiedza, którą posiadasz, jest godna chwały i powinna być przekazywana kolejnym pokoleniom.",
        "Twoja mądrość przypomina mi o jednym z moich najlepszych wojowników, Broði. Jesteś godzien mojego szacunku.",
        "Twoja odpowiedź jest jak łuk skandynawski - mocna i celna. Bogowie powinni być zadowoleni z takiego wyboru.",
        "Zgadzam się z tobą, twoja mądrość przypomina mi o dwóch moich najlepszych wojownikach, Vagni i Haki.",
        "Twoja wiedza o nordyckich mitach jest jak moja broń - niezawodna i potężna.",
        "Twoja odpowiedź jest godna miejsca w Valhalli, zasłużyłeś na niej swoim wysiłkiem i mądrością."
    ]

    WRONG_ANSWER_MESSAGES = [
        "Twoja odpowiedź jest jak marny łuk, niecelna i bez wartości.",
        "Czuję, że powinieneś jeszcze wiele się nauczyć o nordyckich bogach.",
        "Twoja odpowiedź jest fałszywa, bądź ostrożny, by nie oburzyć bogów.",
        "Twoja mądrość przypomina mi o jednym z moich słabszych wojowników.",
        "Twoja odpowiedź jest jak piwo bez alkoholu - bez smaku i bez mocy.",
        "Twoja wiedza o nordyckich mitach jest słaba jak powiew wiatru.",
        "Czuje, że twoja odpowiedź jest wynikiem niezbyt zbyt głębokiej refleksji nad tematem.",
        "Twoja odpowiedź jest jak mój młot, ale bez magii i bez celu.",
        "Twoja wiedza o nordyckich mitach przypomina mi o człowieku, który zagubił się w mroku i nie wie, gdzie się znajduje.",
        "Twoja odpowiedź jest godna potępienia, uważaj, by nie zasłużyć na gniew bogów."
    ]

    @staticmethod
    def load_from_pickle(file_name: str) -> 'Game':
        """
            Loads the game from a pickle file.

            Parameters:
                - file_name: The name of the file.

            Returns:
                The game.
        """
        # If the file does not exist, create a new game and save it to the file.
        logging.info('Game loading from file: ' + file_name)
        if not os.path.exists(file_name):
            logging.info('File does not exist, creating new game.')
            game = Game()
            game.save_to_pickle(file_name)
            return game

        with open(file_name, 'rb') as f:
            return pickle.load(f)

    def save_to_pickle(self, file_name: str):
        """
            Saves the game to a pickle file.

            Parameters:
                - file_name: The name of the file.
        """
        # If the file already exists, rename it (make backup).
        if os.path.exists(file_name):
            os.rename(file_name, file_name +
                      datetime.now().strftime("%d_%m_%y__%H_%M_%S") + '.bak')

        with open(file_name, 'wb') as f:
            pickle.dump(self, f)

        logging.info('Game saved to file: ' + file_name)

    def __init__(self):
        """
            The constructor.
        """
        self.tasks = {}
        self.players = {}
        self.needed_task = {}

    def set_client(self, client: WebClient):
        """
            Sets the client.

            Parameters:
                - client: The client.
        """
        self.client = client

    def add_player(self, user_id: str):
        """
            Adds a player to the game.

            Parameters:
                - user_id: The id of the player.
        """
        if user_id not in self.players:
            self.players[user_id] = Player(user_id)
        logging.info('Player added: ' + user_id)

    def show_players(self) -> str:
        """
            Shows the players.

            Returns:
                The players.
        """
        return ',\n '.join([str(player) for player in self.players.values()])

    def add_task(self, task: Task):
        """
            Adds a task to the game.

            Parameters:
                - task: The task.
        """
        if task.task_no not in self.tasks:
            self.tasks[task.task_no] = task
            if task.needed_task is not None:
                logging.info('Task ' + str(task.task_no) +
                             ' needs task ' + str(task.needed_task))
                self.needed_task[task.needed_task] = task.task_no
        logging.info('Task added: ' + str(task))

    def edit_task(self, task_no: int, **kwargs: Dict[str, Any]):
        """
            Edits a task.

            Parameters:
                - task_no: The number of the task.
                - task: The task.
        """
        if task_no in self.tasks:
            self.tasks[task_no].edit_task(self.client, **kwargs)

    def delete_task(self, task_no: int):
        """
            Deletes a task.

            Parameters:
                - task_no: The number of the task.
        """
        if task_no in self.tasks:
            del self.tasks[task_no]
            # TODO: check how to imlement deleting scheduled tasks, add it as destructor

    def show_tasks(self) -> str:
        """
            Shows the tasks.

            Returns:
                The tasks.
        """
        return ',\n '.join([str(task) for task in self.tasks.values()])

    def complete_task_of_player(self, user_id: str, task_no: int):
        if not task_no in self.players[user_id].completed_tasks:
            self.players[user_id].right_answer(self.tasks[task_no])
            if task_no in self.needed_task:
                self.tasks[self.needed_task[task_no]
                           ].send_task(user_id, self.client)
            logging.info('Task completed: ' +
                         str(task_no) + ' by ' + str(user_id))

    def handle_message(self, message: str, user_id: str, channel: str, task_no: Optional[int] = None, thread_ts: Optional[str] = None):
        """
            Handles the message.

            Parameters:
                - message: The message.
                - user_id: The id of the user.
                - task_no: The number of the task.
                - channel: The channel.
        """
        if task_no is None:
            slack_utils.send_message(self.RANDOM_QUOTES[random.randint(
                0, len(self.RANDOM_QUOTES)-1)], [channel], self.client, thread_ts=[thread_ts])
            logging.info('Random quote sent to OUTER MESSAGE.')
            return MessageType.OUTER_MESSAGE
        elif task_no not in self.tasks:
            slack_utils.send_message("Nie ma takiego zadania.", [
                                     channel], self.client, thread_ts=[thread_ts])
            logging.info('Wrong task number')
            return MessageType.OUTER_MESSAGE
        elif task_no not in self.players[user_id].completed_tasks:
            if self.tasks[task_no].check_answer(message):
                logging.info('Right answer')
                self.players[user_id].right_answer(self.tasks[task_no])
                slack_utils.send_message(self.CORRECT_ANSWER_MESSAGES[random.randint(
                    0, len(self.CORRECT_ANSWER_MESSAGES)-1)], [channel], self.client, thread_ts=[thread_ts])
                if task_no in self.needed_task:
                    logging.info('Sending needed task')
                    self.tasks[self.needed_task[task_no]
                               ].send_task(user_id, self.client)
                return MessageType.RIGHT_ANSWER
            else:
                logging.info('Wrong answer')
                self.players[user_id].wrong_answer(self.tasks[task_no])
                slack_utils.send_message(self.WRONG_ANSWER_MESSAGES[random.randint(
                    0, len(self.WRONG_ANSWER_MESSAGES)-1)], [channel], self.client, thread_ts=[thread_ts])
                return MessageType.WRONG_ANSWER
        else:
            slack_utils.send_message("Na brodę Odyna dzielny wojowniku, już wykonałeś to zadanie.", [
                                     channel], self.client, thread_ts=[thread_ts])
            logging.info('Task already completed')
            return MessageType.OUTER_MESSAGE

    def generate_tasks_view(self) -> str:
        view = '''{
            "title": {
                "type": "plain_text",
                "text": "Podsumowanie zadanek",
                "emoji": true
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Zamknij",
                "emoji": true
            },
            "blocks": [
                '''
        first = True
        for task_no, task in self.tasks.items():
            if not first:
                view += '''
                    ,{
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "''' + str(task) + '''"
                            }
                        ]
                    }
                '''
            else:
                first = False
                view += '''
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "''' + str(task) + '''"
                            }
                        ]
                    }
                '''
        view += "]}"
        return view

    def generate_tasks_list(self) -> str:
        view = ''
        first = True
        for task_no, task in self.tasks.items():
            if not first:
                view += '''
                    ,{
						"text": {
							"type": "plain_text",
							"text": "Task: ''' + str(task_no) + '''",
							"emoji": true
						},
						"value": "''' + str(task_no) + '''"
					}
                '''
            else:
                first = False
                view += '''
                    {
						"text": {
							"type": "plain_text",
							"text": "Task: ''' + str(task_no) + '''",
							"emoji": true
						},
						"value": "''' + str(task_no) + '''"
					}
                '''
        return view

    def generate_players_view(self) -> str:
        view = '''{
            "title": {
                "type": "plain_text",
                "text": "Podsumowanie ludzi",
                "emoji": true
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Zamknij",
                "emoji": true
            },
            "blocks": [
                '''
        first = True
        for user_id, player in self.players.items():
            if not first:
                view += '''
                    ,{
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "''' + str(player) + '''"
                            }
                        ]
                    }
                '''
            else:
                first = False
                view += '''
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "''' + str(player) + '''"
                            }
                        ]
                    }
                '''
        view += "]}"
        return view

    def generate_leaderboard_view(self) -> str:
        view = '''{
            "title": {
                "type": "plain_text",
                "text": "Leaderboard",
                "emoji": true
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Zamknij",
                "emoji": true
            },
            "blocks": [
                '''
        first = True
        for user_id, player in self.players.items():
            player_line = "<@" + user_id + "> - " + \
                str(player.points) + " pkt."
            if not first:
                view += '''
                    ,{
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "''' + player_line + '''"
                            }
                        ]
                    }
                '''
            else:
                first = False
                view += '''
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "''' + player_line + '''"
                            }
                        ]
                    }
                '''
        view += "]}"
        return view
