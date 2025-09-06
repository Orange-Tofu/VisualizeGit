# animations/status.py
import curses
from animations.base import start_animation

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

    # Branch info at top
    window.addstr(1, 2, f"Branch: {state.branch}", curses.color_pair(4))

    # Draw the four boxes (same style as your earlier code)
    draw_box(window, 4, 5, 1, "Untracked",
             [(3, 4, "•"), (3, 6, str(state.untracked))])

    draw_box(window, 4, 25, 2, "Changed",
             [(3, 4, "+"), (3, 6, str(state.changed))])

    draw_box(window, 4, 45, 3, "Staged",
             [(3, 4, "#"), (3, 6, str(state.staged))])

    draw_box(window, 4, 65, 4, "Committed",
             [(3, 3, f"↑{state.ahead}"), (3, 9, f"↓{state.behind}")])

def start(window, git_state):
    return start_animation(window, render, git_state)
