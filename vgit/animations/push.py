# animations/push.py
"""Push animation — visualizes commits moving from local branch to remote."""
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation
from vgit.animations.widgets import draw_box

COMMIT_CHAR = "●"
FLYING_COMMIT_CHAR = "🢂"  # Mirror of fetch
CONNECT = "──"

def _build_commit_chain(n_commits, style):
    """Return a Text object showing n commit nodes linked by arrows."""
    chain = Text()
    for i in range(n_commits):
        chain.append(f" {COMMIT_CHAR} ", style=style)
        if i < n_commits - 1:
            chain.append(CONNECT, style=style)
    return chain

def _build_fly_area(frame, total_steps, start_x=24, end_x=85, vertical_rows=5, state=None):
    """Build a multi-line area with the flying commit at interpolated (x, y).

    Starts at `start_x` (local ref box) and travels to `end_x` (remote branch center).
    """
    step = frame % total_steps
    progress = min(1.0, step / max(total_steps - 1, 1))
    
    # Check if we are in force mode or rejected mode
    is_force = state and getattr(state, "push_type", "") == "force"
    is_rejected = state and getattr(state, "push_type", "") == "rejected"
    is_up_to_date = state and getattr(state, "push_type", "") == "up_to_date"
    
    if is_up_to_date:
        return Group(*[Text("") for _ in range(vertical_rows)])

    # Horizontal: start_x → end_x
    h_pos = int(start_x + (end_x - start_x) * progress)
    
    # Vertical: row vertical_rows-1 (bottom, at box) → row 0 (top)
    v_row = int((vertical_rows - 1) * (1.0 - progress))

    style = "green bold"
    char = FLYING_COMMIT_CHAR
    
    if is_force:
        style = "red bold"
        char = "💨" + FLYING_COMMIT_CHAR # Speed trails
    
    if is_rejected:
        # Phase 1: Forward (0% to 60% of time) -> 0% to 90% travel
        if progress < 0.6:
            p_scaled = progress / 0.6
            p_travel = p_scaled * 0.9
            char = FLYING_COMMIT_CHAR
            style = "green bold"
        else:
            # Phase 2: Backward (60% to 100% of time) -> 90% to 45% travel
            p_scaled = (progress - 0.6) / 0.4
            p_travel = 0.9 - (p_scaled * 0.45) # Halfway back
            char = "🢀"
            style = "red bold"
            
        h_pos = int(start_x + (end_x - start_x) * p_travel)
        v_row = int((vertical_rows - 1) * (1.0 - p_travel))

    lines = []
    for row in range(vertical_rows):
        if row == v_row:
            line = Text()
            line.append(" " * h_pos)
            line.append(char, style=style)
            lines.append(line)
        else:
            lines.append(Text(""))
    return Group(*lines)

def render(state, anim_data):
    """Produce one frame of the push animation as a rich renderable."""
    if "stage" not in anim_data:
        anim_data["stage"] = "pushing"
        anim_data["frame"] = 0
        
    # Determine push type from state
    push_type = getattr(state, "push_type", "normal")
    total_steps = 30 if (push_type == "rejected" or push_type == "force") else 20
    
    tracking_name = getattr(state, "tracking_branch", None)
    ahead = getattr(state, "ahead", 0)

    # ── header ──────────────────────────────────────────────
    action_text = "Force Pushing" if push_type == "force" else "Pushing"
    title = Text(f"{action_text}: {state.branch}", style="bold cyan", justify="center")
    subtitle_txt = (
        f"Remote-tracking: {tracking_name}" if tracking_name else "No remote tracking branch (Creating...)"
    )
    subtitle = Text(subtitle_txt, style="magenta", justify="center")

    # ── side-by-side branches via Table ─────────────────────
    branches_table = Table(
        show_header=False,
        show_edge=False,
        show_lines=False,
        padding=(0, 4),
        expand=True,
    )
    branches_table.add_column("local", ratio=1)
    branches_table.add_column("remote", ratio=1)

    local_label = Text(f"      [Local] ({state.branch}):", style="bold green")
    local_chain = _build_commit_chain(4, "green")
    local_chain.pad_left(6)
    local_col = Group(local_label, local_chain)

    remote_style = "cyan"
    is_upstream = push_type == "upstream"
    
    if (not tracking_name) or (is_upstream and anim_data.get("frame", 0) < total_steps * 0.8):
        # No remote yet, or still 'spawning' in upstream mode
        remote_label_txt = "      [Remote] (New):"
        remote_style = "dim cyan"
        remote_chain = Text("      (creating...)", style="dim italic")
    remote_label_txt = f"      [Remote] {tracking_name or 'origin/' + state.branch}:"
    
    # Destructive visual for Force Push - "shatter" or hide commits during impact
    if push_type == "force" and anim_data.get("frame", 0) > total_steps * 0.95:
        # Show fewer commits or broken chain
        remote_chain = Text("      💥 [OVERWRITING]", style="bold red italic")
    else:
        remote_chain = _build_commit_chain(3, remote_style)
        remote_chain.pad_left(6)
        
    remote_label = Text(remote_label_txt, style=f"bold {remote_style}")
    remote_col = Group(remote_label, remote_chain)

    branches_table.add_row(local_col, remote_col)

    # ── animation body ──────────────────────────────────────
    if push_type == "up_to_date":
        ref_box = draw_box(content_char="✔", style="green")
        note = Text("Everything up-to-date", style="bold green", justify="center")
        body = Group("", ref_box, "", Align.center(note))
    elif anim_data["stage"] == "pushing":
        fly_area = _build_fly_area(
            anim_data["frame"], 
            total_steps=total_steps,
            start_x=24, 
            end_x=85, 
            vertical_rows=5,
            state=state
        )
        ref_box = draw_box()
        
        note_str = "Pushing commits… local data moving to Remote"
        if push_type == "force":
            note_str = "FORCE PUSHING! Overwriting remote history..."
        elif push_type == "rejected":
            note_str = "Push rejected! Non-fast-forward..."
            if anim_data["frame"] > total_steps * 0.6:
                note_str = "ERROR: Fetch and merge remote changes first."
        elif push_type == "upstream":
            note_str = "Setting upstream branch and pushing..."
            if anim_data["frame"] > total_steps * 0.8:
                note_str = "Remote branch created and tracking set!"
        elif not tracking_name:
            note_str = "Pushing to NEW branch on remote..."
            
        note = Text(note_str, style="yellow" if push_type != "rejected" else "red bold", justify="center")

        anim_data["frame"] += 1
        if anim_data["frame"] >= total_steps:
            anim_data["stage"] = "waiting"
            anim_data["wait"] = 0

        body = Group(
            fly_area,
            ref_box,
            "",
            Align.center(note),
        )
    elif anim_data["stage"] == "waiting":
        if push_type == "rejected":
            ref_box = draw_box(content_char="✘", style="red")
            msg = "Push failed: rejected by remote."
            msg_style = "bold red"
        else:
            ref_box = draw_box(content_char="✔", style="green")
            pushed = max(0, ahead)
            msg = f"Pushed {pushed} commit(s) successfully." if pushed > 0 else "Push complete."
            msg_style = "bold green"
            
        msg1 = Text(msg, style=msg_style, justify="center")
        msg2 = Text("Restarting animation...", style="dim italic", justify="center")

        body = Group("", ref_box, "", Align.center(msg1), Align.center(msg2))
        
        anim_data["wait"] += 1
        if anim_data["wait"] >= 25:
            anim_data["stage"] = "pushing"
            anim_data["frame"] = 0
    else:
        body = Group("")

    # ── assemble ────────────────────────────────────────────
    frame_group = Group(
        title,
        subtitle,
        "",
        branches_table,
        body,
    )

    return Panel(frame_group, title="vgit push", border_style="cyan")

def start(layout_pane, git_state):
    """Start the push animation loop."""
    return start_animation(layout_pane, render, git_state)
