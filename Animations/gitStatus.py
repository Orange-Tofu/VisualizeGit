import curses
import logging
import time

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

def draw_box(win, y, x, color, title, symbols):
    win.attron(curses.color_pair(color))
    height, width = 6, 14
    win.addstr(y, x + (width - len(title)) // 2, title)

    win.addstr(y + 1, x, "┌" + "─" * (width - 2) + "┐")
    for i in range(2, height):
        win.addstr(y + i, x, "│" + " " * (width - 2) + "│")
    win.addstr(y + height, x, "└" + "─" * (width - 2) + "┘")

    for sy, sx, sym in symbols:
        win.addstr(y + sy, x + sx, sym)
    
    win.attroff(curses.color_pair(color))

def display_status(window, stop_event):
    curses.curs_set(0)
    curses.start_color()
    
    logging.debug("display_status() started")  
    window.refresh()
    time.sleep(1)

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    while not stop_event.is_set():
        window.clear()
        draw_box(window, 2, 5, 1, "Untracked", [(3, 5, "•"), (4, 4, "•"), (4, 6, "•")])
        draw_box(window, 2, 25, 2, "Staged", [(4, 6, "•")])
        draw_box(window, 2, 45, 3, "Committed", [(4, 6, "#")])
        draw_box(window, 2, 65, 4, "Origin", [(4, 4, "•"), (4, 6, "#")])
        window.refresh()
        curses.napms(500)

    window.clear()
    window.refresh()

# def main():
#     stop_event = threading.Event()

#     def run_curses(stdscr):
#         display_status(stdscr, stop_event)

#     # Start curses in a new thread using wrapper (handles cleanup automatically)
#     curses_thread = threading.Thread(target=curses.wrapper, args=(run_curses,))
#     curses_thread.start()

#     try:
#         # Simulate some work (e.g., running `git status` or waiting for a trigger)
#         time.sleep(10)  # Replace this with your actual condition
#     finally:
#         stop_event.set()
#         curses_thread.join()

# if __name__ == "__main__":
#     main()
