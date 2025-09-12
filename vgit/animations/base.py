# animations/base.py
import threading, time

class AnimationController:
    def __init__(self, stop_event, thread):
        self._stop_event = stop_event
        self._thread = thread

    def stop(self):
        """Stop the animation and wait for thread to finish."""
        self._stop_event.set()
        self._thread.join()

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
    return AnimationController(stop_event, thread)
