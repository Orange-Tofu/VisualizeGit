import curses
import time
import Animations.status as status
from runner import CommandRunner

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    height, width = stdscr.getmaxyx()
    split_point = height // 3

    top_window = curses.newwin(split_point, width, 0, 0)
    bottom_window = curses.newwin(height - split_point, width, split_point, 0)
    bottom_window.scrollok(True)
    bottom_window.idlok(True)

    # Fake git data for top panel
    data = {"untracked": 5, "changed": 3, "staged": 7, "commit": 2}

    # Start command runner for bottom panel
    runner = CommandRunner(["git", "pull"])
    runner.start()

    y = 1
    finished_at = None
    try:
        while True:
            # Update top visualization
            # data["untracked"] += 1
            status.render(top_window, data)

            # Stream bottom output
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

            # If process is done, start countdown
            if not runner.is_running() and finished_at is None:
                finished_at = time.time()

            # Exit if 2 minutes have passed after completion
            if finished_at and time.time() - finished_at > 3:
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

    return runner.captured_lines

if __name__ == "__main__":
    lines = curses.wrapper(main)

    for line in lines:
        print(line, end="")