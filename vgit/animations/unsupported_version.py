# animations/unsupported_version.py
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

ROBOT_ASCII = """
     d[X_X]b
      (   )
       | |
""".strip("\n")

def render(_state=None, _anim_data=None):
    text = Group(
        Align.center(Text(ROBOT_ASCII, style="magenta")),
        "",
        Text("THIS VERSION OF THE COMMAND IS NOT SUPPORTED", justify="center", style="bold red"),
        Text("Kindly run these command in directly with git", justify="center", style="yellow"),
        "",
        Text("We prioritizing standard non-interactive flags like -m", justify="center", style="dim cyan"),
    )
    return Panel(Align.center(text), border_style="red", title="Unsupported Version")

def start(layout_pane, git_state=None):
    return start_animation(layout_pane, render, git_state)
