import curses
import sys
from core import ui_config as cfg

def check_terminal_size(stdscr):
    """
    Ensure the terminal has enough rows/cols for our UI layout.
    If not, exit gracefully with a friendly message.
    """
    rows, cols = stdscr.getmaxyx()

    if rows < cfg.MIN_TERMINAL_HEIGHT or cols < cfg.MIN_TERMINAL_WIDTH:
        curses.endwin()  # clean up curses before printing error
        print(
            f"❌ Terminal too small: {cols}x{rows} "
            f"(minimum {cfg.MIN_TERMINAL_WIDTH}x{cfg.MIN_TERMINAL_HEIGHT} required).\n"
            "👉 Please maximize your terminal and re-run."
        )
        sys.exit(1)
