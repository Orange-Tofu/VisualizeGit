# app.py
import argparse
import ui
from commands import status
import core.ui_utils as ui_utils
import curses

SUPPORTED_COMMANDS = {
    "status": status.run,
}

def main(stdscr):
    ui_utils.check_terminal_size(stdscr)
    
    parser = argparse.ArgumentParser(description="Educational Git Visualizer")
    parser.add_argument("git_command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not args.git_command:
        print("Please provide a git command, e.g. `python app.py status -sb`")
        sys.exit(1)

    subcommand = args.git_command[0]
    full_command = ["git"] + args.git_command

    animation_fn = SUPPORTED_COMMANDS.get(subcommand, ui.unsupported_command_animation)

    ui.start_curses(animation_fn, full_command)

if __name__ == "__main__":
    import sys
    curses.wrapper(main)
