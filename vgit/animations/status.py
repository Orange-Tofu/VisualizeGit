# animations/status.py
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Group

from vgit.animations.base import start_animation

def render(state):
    table = Table(show_header=False, show_edge=False, padding=(1, 2))
    table.add_column("untracked", justify="center")
    table.add_column("changed", justify="center")
    table.add_column("staged", justify="center")
    table.add_column("committed", justify="center")
    
    untracked_panel = Panel(f"• {state.untracked}", title="Untracked", border_style="magenta", expand=False)
    changed_panel = Panel(f"+ {state.changed}", title="Changed", border_style="red", expand=False)
    staged_panel = Panel(f"# {state.staged}", title="Staged", border_style="green", expand=False)
    committed_panel = Panel(f"↑{state.ahead}   ↓{state.behind}", title="Committed", border_style="yellow", expand=False)
    
    table.add_row(untracked_panel, changed_panel, staged_panel, committed_panel)
    
    branch_text = Text(f"Branch: {state.branch}", style="bold yellow")
    note_text = Text("-1 = No remote", style="yellow")
    
    return Panel(
        Group(
            branch_text,
            "",
            Align.center(table),
            "",
            Align.center(note_text)
        ),
        title="Git Status Visualization",
        border_style="blue"
    )

def start(layout_pane, git_state):
    return start_animation(layout_pane, render, git_state)
