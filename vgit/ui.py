# ui.py
import asyncio
from vgit.core.runner import CommandRunner
import vgit.animations.default as default_animation
from rich.console import Console
from rich.layout import Layout
from rich.live import Live

from rich.panel import Panel

def setup_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", ratio=3),
        Layout(name="footer", size=1)
    )
    layout["top"].update(Panel("", border_style="blue"))
    layout["bottom"].update(Panel("", title="Command Output", border_style="blue"))
    layout["footer"].update("")
    return layout

async def wait_for_keypress():
    """Wait for a keypress to exit the UI."""
    try:
        import msvcrt
        while True:
            if msvcrt.kbhit():
                msvcrt.getch()
                break
            await asyncio.sleep(0.05)
    except ImportError:
        # Fallback for non-Windows (though project is focused on Windows)
        # In a real environment, we'd use something cross-platform or raw stdin
        await asyncio.sleep(2.0)

async def start_ui(command_fn, full_command, speed='normal'):
    from rich.align import Align
    from rich.text import Text
    console = Console()
    layout = setup_layout()
    runner = CommandRunner(full_command, layout["bottom"])
    
    with Live(layout, console=console, refresh_per_second=10, screen=True) as live:
        controller = await command_fn(layout["top"], runner, speed=speed)

        layout["footer"].update(Align.right(Text(" Animation looping. Press any key to exit...", style="bold cyan")))
        
        await wait_for_keypress()
        
        if controller:
            await controller.stop()
        
    print("\n".join(runner.get_output()))

async def unsupported_command_animation(top_layout, runner, speed='normal'):
    # default animation needs a state with speed if we want it respects speed
    from vgit.core.git_model import GitState
    dummy_state = GitState(0, 0, 0, "HEAD") # minimal dummy state
    dummy_state.speed = speed
    
    controller = default_animation.start(top_layout, dummy_state)
    await runner.run_and_stream()
    
    return controller


