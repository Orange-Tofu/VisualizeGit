# animations/default.py
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

ROBOT_ASCII = """
   [◉_◉]   
   |   |   
   |___|   
""".strip("\n")

def render(_state=None):
    text = Group(
        Text(ROBOT_ASCII, justify="center", style="cyan"),
        "",
        Text("THIS COMMAND IS NOT SUPPORTED", justify="center", style="bold yellow"),
        Text("Refer to normal command output in terminal below", justify="center", style="yellow"),
        "",
        Text("Want to expand support help? Contribute:", justify="center", style="cyan"),
        Text("https://github.com/Orange-Tofu/VisualizeGit", justify="center", style="underline cyan")
    )
    return Panel(Align.center(text), border_style="red", title="Not Supported")

def start(layout_pane, _git_state=None):
    return start_animation(layout_pane, render, None)
