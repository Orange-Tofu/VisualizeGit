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

async def start_ui(command_fn, full_command, speed='normal'):
    console = Console()
    layout = setup_layout()
    runner = CommandRunner(full_command, layout["bottom"])
    
    with Live(layout, console=console, refresh_per_second=10, screen=True) as live:
        await command_fn(layout["top"], runner, speed=speed)
        
    print("\n".join(runner.get_output()))

async def unsupported_command_animation(top_layout, runner, speed='normal'):
    # default animation needs a state with speed if we want it respects speed
    from vgit.core.git_model import GitState
    dummy_state = GitState(0, 0, 0, "HEAD") # minimal dummy state
    dummy_state.speed = speed
    
    controller = default_animation.start(top_layout, dummy_state)
    await runner.run_and_stream()
    
    pause = 3.0 if speed == 'normal' else (1.5 if speed == 'fast' else 6.0)
    await asyncio.sleep(pause)
    await controller.stop()


