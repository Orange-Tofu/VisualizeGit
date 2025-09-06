# ui.py
import curses

def setup_windows(stdscr):
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()
    split_point = height // 3

    top_window = curses.newwin(split_point, width, 0, 0)
    bottom_window = curses.newwin(height - split_point, width, split_point, 0)
    return top_window, bottom_window

def start_curses(command_fn):
    def wrapped(stdscr):
        top, bottom = setup_windows(stdscr)
        command_fn(top, bottom)
    curses.wrapper(wrapped)
