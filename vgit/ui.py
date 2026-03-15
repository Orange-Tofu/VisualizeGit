# ui.py
from vgit.core.runner import CommandRunner
import vgit.animations.default as default_animation
import time
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

def setup_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", ratio=3)
    )
    return layout

def start_ui(command_fn, full_command):
    console = Console()
    layout = setup_layout()
    runner = CommandRunner(full_command, layout["bottom"])
    
    with Live(layout, console=console, refresh_per_second=10, screen=True) as live:
        command_fn(layout["top"], runner)
        
    print("\n".join(runner.get_output()))

def unsupported_command_animation(top_layout, runner):
    controller = default_animation.start(top_layout)
    runner.run_and_stream()
    time.sleep(5)
    controller.stop()


