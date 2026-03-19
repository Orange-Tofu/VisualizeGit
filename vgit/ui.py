# ui.py
import asyncio
from vgit.core.runner import CommandRunner
import vgit.animations.default as default_animation
from rich.console import Console
from rich.layout import Layout
from rich.live import Live

def setup_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", ratio=3)
    )
    return layout

async def start_ui(command_fn, full_command):
    console = Console()
    layout = setup_layout()
    runner = CommandRunner(full_command, layout["bottom"])
    
    with Live(layout, console=console, refresh_per_second=10, screen=True) as live:
        await command_fn(layout["top"], runner)
        
    print("\n".join(runner.get_output()))

async def unsupported_command_animation(top_layout, runner):
    controller = default_animation.start(top_layout)
    await runner.run_and_stream()
    await asyncio.sleep(3)
    await controller.stop()




