# animations/base.py
import threading
import time

def start_animation(window, render_fn, git_state):
    stop_event = threading.Event()

    def run():
        while not stop_event.is_set():
            window.clear()
            render_fn(window, git_state)
            window.refresh()
            time.sleep(0.5)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return stop_event, thread
