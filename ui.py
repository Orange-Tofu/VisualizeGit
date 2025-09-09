# ui.py
import curses
from core.runner import CommandRunner
import animations.default as default_animation
import time

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
    stop_event, anim_thread = default_animation.start(window)
    runner.run_and_stream()
    time.sleep(5)
    stop_event.set()
    anim_thread.join()
    print("\n".join(runner.get_output()))
