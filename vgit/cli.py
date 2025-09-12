# cli.py

import argparse
import ui
from .commands import status, fetch, commit
import core.ui_utils as ui_utils
import curses

SUPPORTED_COMMANDS = {
    "status": status.run,
    "fetch": fetch.run,
    "commit": commit.run
}

def main():
    """
    CLI entry point for vgit.
    """
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

    def wrapped(stdscr):
        # terminal size & window setup
        ui_utils.check_terminal_size(stdscr)
        top, bottom = ui_utils.setup_windows(stdscr)
        runner = CommandRunner(full_command, bottom)
        animation_fn(top, runner)

    curses.wrapper(wrapped)