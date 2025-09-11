# animations/status.py
import curses
from animations.base import start_animation
from core import ui_config as cfg

def draw_box(win, y, x, color, title, symbols):
    """
    Draws an individual box with title and content.
    """
    win.attron(curses.color_pair(color))
    height, width = 6, 14

    # Title centered
    win.addstr(y, x + (width - len(title)) // 2, title)

    # Box outline
    win.addstr(y + 1, x, "┌" + "─" * (width - 2) + "┐")
    for i in range(2, height):
        win.addstr(y + i, x, "│" + " " * (width - 2) + "│")
    win.addstr(y + height, x, "└" + "─" * (width - 2) + "┘")

    # Symbols inside
    for sy, sx, sym in symbols:
        win.addstr(y + sy, x + sx, sym)

    win.attroff(curses.color_pair(color))

def render(window, state):
    """
    Render git status visualization using boxes.
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    # Clear and draw border for top window
    window.clear()
    window.box()

    window.addstr(1, 2, f"Branch: {state.branch}", curses.color_pair(4))

    draw_box(
        window, cfg.ROW_Y, cfg.STATUS_X_POSITIONS["untracked"],
        cfg.STATUS_COLORS["magenta"], "Untracked",
        [(3, 4, "•"), (3, 6, str(state.untracked))]
    )

    draw_box(
        window, cfg.ROW_Y, cfg.STATUS_X_POSITIONS["changed"],
        cfg.STATUS_COLORS["red"], "Changed",
        [(3, 4, "+"), (3, 6, str(state.changed))]
    )

    draw_box(
        window, cfg.ROW_Y, cfg.STATUS_X_POSITIONS["staged"],
        cfg.STATUS_COLORS["green"], "Staged",
        [(3, 4, "#"), (3, 6, str(state.staged))]
    )

    draw_box(
        window, cfg.ROW_Y, cfg.STATUS_X_POSITIONS["committed"],
        cfg.STATUS_COLORS["yellow"], "Committed",
        [(3, 3, f"↑{state.ahead}"), (3, 9, f"↓{state.behind}")]
    )

    window.addstr(cfg.BOTTOM_ROW_TEXT_Y, cfg.STATUS_X_POSITIONS["committed"] + 1, "-1 = No remote", curses.color_pair(cfg.STATUS_COLORS["yellow"]))

def start(window, git_state):
    return start_animation(window, render, git_state)
