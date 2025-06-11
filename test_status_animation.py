from Animations.gitStatus import display_status as display_status;
import time
import curses
import threading

def main():
    stop_event = threading.Event()

    def run_curses(stdscr):
        display_status(stdscr, stop_event)

    # Start curses in a new thread using wrapper (handles cleanup automatically)
    curses_thread = threading.Thread(target=curses.wrapper, args=(run_curses,))
    curses_thread.start()

    try:
        # Simulate some work (e.g., running `git status` or waiting for a trigger)
        time.sleep(10)  # Replace this with your actual condition
    finally:
        stop_event.set()
        curses_thread.join()

if __name__ == "__main__":
    main()