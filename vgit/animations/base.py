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

    def is_stopped(self):
        """Return True if the animation has been requested to stop."""
        return self._stop_event.is_set()

def start_animation(window, render_fn, git_state):
    stop_event = threading.Event()

    def run():
        # Make key reads non-blocking so we can detect SPACE to exit
        try:
            window.nodelay(True)
        except Exception:
            pass
        while not stop_event.is_set():
            window.clear()
            render_fn(window, git_state)
            window.refresh()
            # Check for SPACE (or 'q') to stop
            try:
                ch = window.getch()
                if ch in (32, ord('q')):  # SPACE or 'q'
                    stop_event.set()
                    break
            except Exception:
                # Ignore getch errors (e.g., window too small)
                pass
            time.sleep(0.5)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return AnimationController(stop_event, thread)
