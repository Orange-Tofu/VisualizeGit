# animations/default.py
import curses
from animations.base import start_animation
from core import ui_config as cfg

ROBOT_ASCII = """
   [◉_◉]   
   |   |   
   |___|   
""".strip("\n")

def render(window, _state=None):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    window.clear()
    window.box()

    height, width = window.getmaxyx()

    # Draw robot head on the left
    start_y = 2
    for i, line in enumerate(ROBOT_ASCII.splitlines()):
        window.addstr(start_y + i, 4, line, curses.color_pair(1))

    # Main title + subtitle
    msg1 = "THIS COMMAND IS NOT SUPPORTED"
    msg2 = "Refer to normal command output in terminal below"

    window.addstr(3, (width - len(msg1)) // 2, msg1, curses.color_pair(2) | curses.A_BOLD)
    window.addstr(5, (width - len(msg2)) // 2, msg2, curses.color_pair(2))

    # Footer contribution message
    footer1 = "Want to expand support help? Contribute:"
    footer2 = "github.com/yourrepo"

    window.addstr(height - 4, (width - len(footer1)) // 2, footer1, curses.color_pair(1))
    window.addstr(height - 3, (width - len(footer2)) // 2, footer2, curses.color_pair(1) | curses.A_UNDERLINE)

    window.refresh()

def start(window, _git_state=None):
    # fallback animation doesn't depend on repo state
    return start_animation(window, render, None)
