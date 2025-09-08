# core/runner.py
import subprocess
import time

class CommandRunner:
    def __init__(self, cmd, window):
        self.cmd = cmd
        self.window = window
        self.output_lines = []
        self._process = None

    def run_and_stream(self):
        """Run the git command and stream live output into the window."""
        self._process = subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for line in self._process.stdout:
            self.output_lines.append(line.rstrip())
            try:
                self.window.addstr(line)
                self.window.refresh()
            except Exception:
                # prevent curses crash if line is too long
                pass

        self._process.wait()
        return self._process.returncode, self.output_lines

    def process_running(self):
        """Check if process is still active."""
        return self._process and self._process.poll() is None

    def get_output(self):
        """Get collected output lines."""
        return self.output_lines
