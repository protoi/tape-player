import threading
from StateMachine import StateMachine


class HandleUserInput:

    def __init__(self, tape_player_state_machine: StateMachine) -> None:
        self.state_machine = tape_player_state_machine

    def consume_user_input(self) -> None:
        """looping forever and consuming user inputs. An input of k will kill the process
        """
        while True:
            try:
                action_to_perform = input(
                    "\np: PLAY | s: STOP | r: REWIND | f: FASTFORWARD | k: KILL\n")
                if action_to_perform == 'k':
                    print("KILLED :-)")
                    return
                self.state_machine.handle_state_transition(action_to_perform)
            except:
                print("Failed to transition :-(")

    def start_user_input(self) -> None:
        """Starts a thread to consume user inputs
        """
        self.USER_INPUT = threading.Thread(target=self.consume_user_input)
        self.USER_INPUT.start()
