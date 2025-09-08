# ui.py
import curses
from core.runner import CommandRunner

def setup_windows(stdscr):
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()
    split_point = (2 * height) // 5

    top_window = curses.newwin(split_point, width, 0, 0)
    bottom_window = curses.newwin(height - split_point, width, split_point, 0)
    return top_window, bottom_window

def start_curses(command_fn, full_command):
    def wrapped(stdscr):
        top, bottom = setup_windows(stdscr)
        runner = CommandRunner(full_command, bottom)
        command_fn(top, runner)
    curses.wrapper(wrapped)

def unsupported_command_animation(window, runner):
    window.clear()
    window.box()
    msg = "This command is not currently supported for visualization.\n"
    msg += "Please refer to the terminal output below."
    window.addstr(2, 2, msg)
    window.refresh()

    runner.run_and_stream()
