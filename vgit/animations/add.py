# animations/add.py
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

FILE_ICON = "📄"
ARROW = "──▶"

def _render_files_list(count, title, color):
    """Render a box with file count and some icons."""
    icons = f" {FILE_ICON} " * min(count, 5)
    if count > 5:
        icons += "..."
    elif count == 0:
        icons = "(empty)"
    
    return Panel(
        Group(
            "",
            Align.center(Text(str(count), style=f"bold {color}")),
            Align.center(Text(icons, style=color)),
            ""
        ),
        title=f"[bold {color}]{title}[/]",
        border_style=color,
        width=25
    )

def render(state, anim_data):
    """Render the add animation frame."""
    if "frame" not in anim_data:
        anim_data["frame"] = 0
    if "stage" not in anim_data:
        anim_data["stage"] = "adding"
        
    frame = anim_data["frame"]
    
    # State info
    unstaged_count = getattr(state, "changed", 0) + getattr(state, "untracked", 0)
    staged_count = getattr(state, "staged", 0)
    to_add_count = getattr(state, "to_add_count", 0)
    add_status = getattr(state, "add_status", "running")
    
    if anim_data["stage"] == "adding":
        unstaged_count = getattr(state, "initial_unstaged", unstaged_count)
        staged_count = getattr(state, "initial_staged", staged_count)
        
    # Panels
    unstaged_panel = _render_files_list(unstaged_count, "Unstaged", "red")
    staged_panel = _render_files_list(staged_count, "Staged", "green")
    
    total_steps = 15 # Shorter bursts for 'add'
    
    GAP_WIDTH = 40
    if anim_data["stage"] == "adding":
        step = frame % total_steps
        progress = step / total_steps
        
        # Flying icon in the gap
        trail = f"{ARROW} {FILE_ICON} {ARROW}"
        trail_len = 10 # Estimated visual width
        
        # Start X pos: 0 -> GAP_WIDTH - trail_len
        max_pos = GAP_WIDTH - trail_len
        pos = int(max_pos * progress)
        
        fly_line = Text()
        fly_line.append(" " * pos)
        fly_line.append(trail, style="cyan bold")
        # Pad to full GAP_WIDTH to ensure it never changes the overall layout
        fly_line.append(" " * (GAP_WIDTH - pos - trail_len))
        
        note = Text(f"Staging {to_add_count} file(s)...", style="yellow")
        
        anim_data["frame"] += 1
        if add_status != "running" and step == total_steps - 1:
             anim_data["stage"] = "done"
             anim_data["wait"] = 0

    elif anim_data["stage"] == "done":
        fly_line = Text("✔".center(GAP_WIDTH), style="bold green")
        
        if add_status == "success":
            note = Text(f"Successfully staged {to_add_count} file(s)!", style="bold green")
        else:
            note = Text("Add failed or nothing to add.", style="bold red")
            
        anim_data["wait"] += 1
        if anim_data["wait"] > 25:
            anim_data["stage"] = "adding"
            anim_data["frame"] = 0
            
    table = Table.grid(padding=(0, 2))
    table.add_column(width=25) # Unstaged Column
    table.add_column(width=GAP_WIDTH) # Flight Column
    table.add_column(width=25) # Staged Column
    table.add_row(unstaged_panel, Align(fly_line, align="center", vertical="middle"), staged_panel)
    
    return Panel(
        Group(
            "",
            Align.center(table),
            "",
            Align.center(note),
            "",
            Align.center(Text("Restarting animation...", style="dim italic") if anim_data.get("stage") == "done" else Text(""))
        ),
        title="vgit add",
        border_style="blue"
    )

def start(layout_pane, git_state):
    """Initialize and start the add animation."""
    return start_animation(layout_pane, render, git_state)
