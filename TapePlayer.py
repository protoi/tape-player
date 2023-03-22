from UserInput import HandleUserInput
from StateMachine import StateMachine

if __name__ == "__main__":
    """Runner for the Tape Player
    """
    tape_len = int(input("Enter the tape length: "))

    tape = StateMachine(abs(tape_len))
    tape.handle_start_tape()

    input_handler = HandleUserInput(tape)
    input_handler.start_user_input()
