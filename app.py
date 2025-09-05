import sys
import curses
import time
from core.runner import CommandRunner
from core.ui import split_screen
import animations.status as status
# future: import Animations.pull as pull, Animations.push as push, etc.

COMMANDS = {
    "status": status.render,
    # "pull": pull.render,
    # "push": push.render,
}

def main(stdscr, action, git_args):
    top_window, bottom_window = split_screen(stdscr)

    # Construct full git command
    command = ["git", action] + git_args
    runner = CommandRunner(command)
    runner.start()

    # Example data dict (could be updated live from git output later)
    data = {"untracked": 0, "changed": 0, "staged": 0, "commit": 0}
    y = 1
    finished_at = None

    while True:
        # Call the relevant animation for the action
        COMMANDS[action](top_window, data)

        # Stream git output into bottom window
        line = runner.poll_line()
        while line:
            max_y, max_x = bottom_window.getmaxyx()
            if y >= max_y - 1:
                bottom_window.scroll(1)
                y = max_y - 2
            bottom_window.addnstr(y, 2, line.rstrip(), max_x - 4)
            y += 1
            bottom_window.refresh()
            line = runner.poll_line()

        # Grace period after process ends
        if not runner.is_running() and finished_at is None:
            finished_at = time.time()
        if finished_at and time.time() - finished_at > 3:
            break

        curses.napms(100)

    return runner.captured_lines

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <command> [git-options...]")
        sys.exit(1)

    action = sys.argv[1]
    git_args = sys.argv[2:]

    if action not in COMMANDS:
        print(f"Unknown command: {action}")
        sys.exit(1)

    lines = curses.wrapper(main, action, git_args)
    for line in lines:
        print(line, end="")
