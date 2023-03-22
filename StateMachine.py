import os
import threading
import time
from math import floor


class StateMachine:
    def __init__(self, tape_length) -> None:
        # region Tape Player Properties
        self.FF_SPEED = 10
        self.REWIND_SPEED = -10
        self.STEP = 1
        self.tape_length = tape_length
        self.tape_traversed_so_far = 0
        # endregion

        self.finished_playing = False
        self.initialized = False

        self.player_lock = threading.Lock()

        # region Constants

        self.PLAYING, self.STOPPED, self.FAST_FORWARDING, self.REWINDING = 1, 2, 3, 4
        self.CURRENT_STATE = self.STOPPED
        # mapping of current state, input -> new state
        self.ACTION_MAPPING = {
            (self.PLAYING, "p"): self.PLAYING,
            (self.PLAYING, "s"): self.STOPPED,
            (self.PLAYING, "f"): self.FAST_FORWARDING,
            (self.PLAYING, "r"): self.REWINDING,

            (self.STOPPED, "p"): self.PLAYING,
            (self.STOPPED, "s"): self.STOPPED,
            (self.STOPPED, "f"): self.FAST_FORWARDING,
            (self.STOPPED, "r"): self.REWINDING,

            (self.FAST_FORWARDING, "p"): self.PLAYING,
            (self.FAST_FORWARDING, "s"): self.STOPPED,
            (self.FAST_FORWARDING, "f"): self.FAST_FORWARDING,
            (self.FAST_FORWARDING, "r"): self.REWINDING,

            (self.REWINDING, "p"): self.PLAYING,
            (self.REWINDING, "s"): self.STOPPED,
            (self.REWINDING, "f"): self.FAST_FORWARDING,
            (self.REWINDING, "r"): self.REWINDING,
        }

        # text to display
        self.STATE_NAME_MAPPING = {
            self.PLAYING: "Playing",
            self.STOPPED: "Paused",
            self.FAST_FORWARDING: "Fast Forwarding",
            self.REWINDING: "Rewinding"
        }

        # rate at which the tape player will proceed at every state

        self.STATE_PROGRESS_MAPPING = {
            self.PLAYING: 1,
            self.STOPPED: 0,
            self.FAST_FORWARDING: self.FF_SPEED,
            self.REWINDING: self.REWIND_SPEED
        }

        # endregion

    def format_seconds_as_mm_ss(self, length_in_seconds) -> str:
        """converts time in seconds to minute : second format

        Args:
            length_in_seconds (int): time in

        Returns:
            str: formatted time
        """
        min, sec = divmod(length_in_seconds, 60)
        return f"{min}:{sec}"

    def handle_state_transition(self, userInput: str) -> None:
        """Updates state of the Tape Player

        Args:
            userInput (str): input provided by the user, valid inputs are p,s,r and f
        """
        next_state = self.ACTION_MAPPING.get(
            (self.CURRENT_STATE, userInput), -1)
        if next_state == -1:  # no state transition possible for this given input
            print("\ninvalid command\n\n")
            return
        with self.player_lock:
            self.CURRENT_STATE = next_state

    def handle_start_tape(self) -> None:
        """Starts a thread for playing the tape
        """
        self.CURRENT_STATE = self.STOPPED
        self.TAPE_PLAYER = threading.Thread(target=self.traverse_tape)
        # self.TAPE_PLAYER.daemon = True
        self.TAPE_PLAYER.start()

    def display_status(self) -> None:
        """format and print the current time, remaining time and progresso of the tape player
        """
        fraction_completed = self.tape_traversed_so_far / self.tape_length
        display_length = 10
        display_completed = floor(display_length * fraction_completed)

        viewed, remaining = "=", "."

        player_bar = f"{viewed * (display_completed-1) }\
{'<' if self.CURRENT_STATE == self.REWINDING else '>'}\
{ remaining * (display_length - display_completed)}"

        # displaying the status of the player
        print(
            f"{self.STATE_NAME_MAPPING.get(self.CURRENT_STATE, 'Nothing')}:\n\
{self.format_seconds_as_mm_ss(self.tape_traversed_so_far)} \
| {player_bar} | \
{self.format_seconds_as_mm_ss(self.tape_length)}\n")

    def traverse_tape(self) -> None:
        """Looping time the entire tape has been covered
        """
        while self.tape_traversed_so_far < self.tape_length:
            with self.player_lock:
                # region Updating progression of the tape
                progression = self.STATE_PROGRESS_MAPPING.get(
                    self.CURRENT_STATE, 0)
                self.tape_traversed_so_far += progression * self.STEP

                # preventing overflows and underflows
                self.tape_traversed_so_far = min(
                    self.tape_length, self.tape_traversed_so_far)
                self.tape_traversed_so_far = max(
                    0, self.tape_traversed_so_far)
                # endregion
                if self.CURRENT_STATE != self.STOPPED:
                    self.display_status()

            # waiting for a second
            time.sleep(1)
        self.finished_playing = True
        print("finished playing :-)")
        os._exit(0)
