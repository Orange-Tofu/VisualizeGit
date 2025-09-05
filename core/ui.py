import curses

def split_screen(stdscr):
    height, width = stdscr.getmaxyx()
    split_point = height // 3

    top_window = curses.newwin(split_point, width, 0, 0)
    bottom_window = curses.newwin(height - split_point, width, split_point, 0)
    bottom_window.scrollok(True)
    bottom_window.idlok(True)

    return top_window, bottom_window
