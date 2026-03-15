# core/runner.py
import subprocess
import time
from rich.panel import Panel
from rich.text import Text

class CommandRunner:
    def __init__(self, cmd, layout_pane):
        self.cmd = cmd
        self.layout_pane = layout_pane
        self.output_lines = []
        self._process = None

    def run_and_stream(self):
        """Run the git command and stream live output into the layout pane."""
        self._process = subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace'
        )

        for line in self._process.stdout:
            self.output_lines.append(line.rstrip())
            # Keep only the last N lines to prevent layout overflow, or just show all in a Panel
            # Let's show the last 50 lines
            display_text = "\n".join(self.output_lines[-50:])
            # Update the layout pane (Live will automatically redraw it)
            self.layout_pane.update(Panel(Text(display_text), title="Command Output", border_style="blue"))

        self._process.wait()
        return self._process.returncode, self.output_lines

    def process_running(self):
        """Check if process is still active."""
        return self._process and self._process.poll() is None

    def get_output(self):
        """Get collected output lines."""
        return self.output_lines
