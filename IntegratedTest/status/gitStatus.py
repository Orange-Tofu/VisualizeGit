import curses
import time

def draw_box(win, y, x, color, title, symbols):
    """Draws a colored box with a title and symbols inside."""
    win.attron(curses.color_pair(color))
    height, width = 6, 14  # Box dimensions
    win.addstr(y, x + (width - len(title)) // 2, title)  # Title centered
    
    # Draw the box
    for i in range(height):
        win.addstr(y + i + 1, x, " " + (" " * (width - 2)) + " ")
    
    # Draw borders manually for better control
    win.addstr(y + 1, x, "┌" + "─" * (width - 2) + "┐")
    for i in range(2, height):
        win.addstr(y + i, x, "│" + " " * (width - 2) + "│")
    win.addstr(y + height, x, "└" + "─" * (width - 2) + "┘")

    # Place symbols inside the box
    for sy, sx, sym in symbols:
        win.addstr(y + sy, x + sx, sym)
    
    win.attroff(curses.color_pair(color))

def display_status(stdscr, stop_event):
    curses.curs_set(0)
    curses.start_color()
    
    # Debugging print
    print("display_status() started")  
    stdscr.refresh()
    time.sleep(5)  # Delay to observe behavior
    print("display_status() exiting")  
    
    # Define color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    while not stop_event.is_set():  # Stop when git status is done
        stdscr.clear()
        
        # Draw the four git status boxes
        draw_box(stdscr, 2, 5, 1, "Untracked", [(2, 5, "•"), (3, 4, "•"), (3, 6, "•")])
        draw_box(stdscr, 2, 25, 2, "Staged", [(3, 6, "•")])
        draw_box(stdscr, 2, 45, 3, "Committed", [(3, 6, "#")])
        draw_box(stdscr, 2, 65, 4, "Origin", [(3, 4, "•"), (3, 6, "#")])

        stdscr.refresh()
        
        # Add a small delay to prevent CPU overuse
        curses.napms(500)  # Sleep for 500ms

    stdscr.clear()  # Clear the animation when done
    stdscr.refresh()

if __name__ == "__main__":
    import threading
    import time

    def test(stdscr):
        stop_event = threading.Event()
        t = threading.Thread(target=display_status, args=(stdscr, stop_event))
        t.start()
        time.sleep(5)  # Simulate git status running for 5 seconds
        stop_event.set()
        t.join()

    curses.wrapper(test)
