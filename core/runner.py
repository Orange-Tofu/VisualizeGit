# core/runner.py
import subprocess

def run_command(cmd, window):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    output_lines = []
    for line in process.stdout:
        output_lines.append(line.rstrip())
        window.addstr(line)
        window.refresh()

    process.wait()
    return output_lines
