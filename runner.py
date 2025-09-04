import subprocess
import threading
import queue

class CommandRunner:
    def __init__(self, command):
        self.command = command
        self.queue = queue.Queue()
        self.proc = None
        self.thread = None

    def start(self):
        def reader(proc, q):
            for line in iter(proc.stdout.readline, ''):
                q.put(line)
            proc.stdout.close()

        self.proc = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,   # decode as str automatically
        )

        self.thread = threading.Thread(target=reader, args=(self.proc, self.queue), daemon=True)
        self.thread.start()

    def poll_line(self):
        """Return one line if available, else None"""
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None

    def is_running(self):
        return self.proc and self.proc.poll() is None
