import curses
import time

def main(stdscr):
    # Initialize the screen
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Refresh interval

    # Initialize color functionality
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Define color pair

    color_pair = curses.color_pair(1)  # Get the color pair

    x, y = 10, 10
    dx, dy = 1, 1

    while True:
        stdscr.clear()  # Clear the screen
        stdscr.addstr(y, x, "Hello!", color_pair)  # Print text with color
        stdscr.refresh()  # Refresh the screen

        x += dx
        y += dy

        if x == curses.COLS - 1 or x == 0:
            dx *= -1
        if y == curses.LINES - 1 or y == 0:
            dy *= -1

        time.sleep(0.05)  # Delay to make the animation visible

# Run the curses wrapper
curses.wrapper(main)
