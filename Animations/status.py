import curses

def render(window, data):
    """
    Draw git status boxes into the given window.
    """
    window.erase()
    window.box()

    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    def draw_box(y, x, color, title, symbols):
        window.attron(curses.color_pair(color))
        height, width = 6, 14
        window.addstr(y, x + (width - len(title)) // 2, title)
        window.addstr(y + 1, x, "┌" + "─" * (width - 2) + "┐")
        for i in range(2, height):
            window.addstr(y + i, x, "│" + " " * (width - 2) + "│")
        window.addstr(y + height, x, "└" + "─" * (width - 2) + "┘")
        for sy, sx, sym in symbols:
            window.addstr(y + sy, x + sx, sym)
        window.attroff(curses.color_pair(color))

    draw_box(2, 5, 1, "Untracked", [(3, 4, "•"), (3, 6, str(data.get("untracked", 0)))])
    draw_box(2, 25, 2, "Changed", [(3, 4, "+"), (3, 6, str(data.get("changed", 0)))])
    draw_box(2, 45, 3, "Staged", [(3, 4, "#"), (3, 6, str(data.get("staged", 0)))])
    draw_box(2, 65, 4, "Committed", [(3, 4, "✓"), (3, 7, str(data.get("commit", 0)))])

    window.refresh()
