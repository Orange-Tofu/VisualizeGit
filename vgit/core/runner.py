# core/runner.py
import asyncio
from rich.panel import Panel
from rich.text import Text

class CommandRunner:
    def __init__(self, cmd, layout_pane):
        self.cmd = cmd
        self.layout_pane = layout_pane
        self.output_lines = []
        self._process = None

    async def run_and_stream(self):
        """Run the git command and stream live output into the layout pane."""
        # Split command into program and args for create_subprocess_exec
        program = self.cmd[0]
        args = self.cmd[1:]
        
        self._process = await asyncio.create_subprocess_exec(
            program,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await self._process.stdout.readline()
            if not line:
                break
            
            decoded_line = line.decode('utf-8', errors='replace').rstrip()
            self.output_lines.append(decoded_line)
            
            # Show the last 50 lines
            display_text = "\n".join(self.output_lines[-50:])
            # Update the layout pane
            self.layout_pane.update(Panel(Text(display_text), title="Command Output", border_style="blue"))

        await self._process.wait()
        return self._process.returncode, self.output_lines

    def process_running(self):
        """Check if process is still active."""
        return self._process and self._process.returncode is None

    def get_output(self):
        """Get collected output lines."""
        return self.output_lines
