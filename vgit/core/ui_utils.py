import curses
import sys
from vgit.core import ui_config as cfg

def check_terminal_size(stdscr):
    """
    Ensure the terminal has enough rows/cols for our UI layout.
    If not, exit gracefully with a friendly message.
    """
    rows, cols = stdscr.getmaxyx()
    if rows < 20 or cols < 80:
        curses.endwin()  # clean up curses before printing error
        print(
            f"❌ Terminal too small: {cols}x{rows} "
            f"(minimum {cfg.MIN_TERMINAL_WIDTH}x{cfg.MIN_TERMINAL_HEIGHT} required).\n"
            "👉 Please maximize your terminal and re-run."
        )
        sys.exit(1)


def wait_for_button_press(window):
    """
    Wait for user to press SPACE or ENTER to continue.
    """

    while True:
            msg = "Press SPACE or ENTER to continue..."
            h, w = window.getmaxyx()

            try:
                window.addstr(h - 2, max(2, (w - len(msg)) // 2), msg)
            except Exception:
                pass

            window.refresh()
            key = window.getch()
            if key in (32, 10):  # SPACE=32, ENTER=10
                break