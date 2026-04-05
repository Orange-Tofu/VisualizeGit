# animations/pull.py
"""Pull animation — visualizes fetch + integration (merge/rebase)."""
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation
from vgit.animations.widgets import draw_box

COMMIT_CHAR = "●"
FLYING_COMMIT_CHAR = "🢀"
CONNECT = "──"
MERGE_CHAR = "◆"

def _build_commit_chain(n_commits, style, head_char=COMMIT_CHAR, new_commits=0, new_style="bold magenta"):
    """Return a Text object showing n commit nodes linked by connectors."""
    chain = Text()
    # Original commits
    for i in range(n_commits):
        char = head_char if (i == n_commits - 1 and new_commits == 0) else COMMIT_CHAR
        chain.append(f" {char} ", style=style)
        if i < n_commits - 1 or new_commits > 0:
            chain.append(CONNECT, style=style)
    
    # New commits from pull
    for i in range(new_commits):
        char = MERGE_CHAR if (i == new_commits - 1) else COMMIT_CHAR
        chain.append(f" {char} ", style=new_style)
        if i < new_commits - 1:
            chain.append(CONNECT, style=new_style)
    return chain

def _build_fly_area(frame, total_steps, start_x=85, end_x=24, vertical_rows=3, char=FLYING_COMMIT_CHAR, style="red bold"):
    """Build a multi-line area with a flying commit at interpolated (x, y)."""
    step = frame % total_steps
    progress = min(1.0, step / max(total_steps - 1, 1))
    h_pos = int(start_x - (start_x - end_x) * progress)
    v_row = int((vertical_rows - 1) * progress)

    lines = []
    for row in range(vertical_rows):
        if row == v_row:
            line = Text(" " * h_pos)
            line.append(char, style=style)
            lines.append(line)
        else:
            lines.append(Text(""))
    return Group(*lines)

def _build_integration_area(frame, total_steps, pull_type, vertical_rows=3):
    """Visualizes 3-way merge, rebase, or FF integration."""
    step = frame % total_steps
    progress = min(1.0, step / max(total_steps - 1, 1))
    lines = [Text("") for _ in range(vertical_rows)]

    if pull_type == "merge":
        # 3-way merge: Local (x=24, Top) and Ref Box (x=24, Bottom) converge rightward to x=40
        center_x = 40
        if progress < 0.7:
             p_scaled = progress / 0.7
             x_pos = int(24 + (center_x - 24) * p_scaled)
             v_top = int(1 * p_scaled)       # 0 down to 1
             v_bot = int(2 - 1 * p_scaled)   # 2 up to 1
             if v_top == 1 and v_bot == 1:
                  lines[1] = Text(" " * x_pos + MERGE_CHAR, style="bold cyan")
             else:
                  lines[v_top] = Text(" " * x_pos + "●", style="green")
                  lines[v_bot] = Text(" " * x_pos + "●", style="cyan")
        else:
             lines[1] = Text(" " * center_x + MERGE_CHAR, style="bold magenta")
             lines[0] = Text(" " * 24 + "╰" + "─" * (center_x - 25) + "╮", style="dim white")
             lines[2] = Text(" " * 24 + "╭" + "─" * (center_x - 25) + "╯", style="dim white")

    elif pull_type == "rebase":
        # Rebase: Ref Box commits moving UP, Local commits detached
        v_idx = int(2 * (1.0 - progress)) # Fly UP from 2 to 0
        lines[v_idx] = Text(" " * 24 + "🢁 (replaying local on top)", style="bold cyan")

    elif pull_type == "collision":
        # Strictly vertical collision on the local side (x=24)
        v_top = int(1 * progress)       # 0 down toward middle
        v_bot = int(2 - 1 * progress)   # 2 up toward middle
        if progress < 0.9:
             if v_top != v_bot:
                  lines[v_top] = Text(" " * 24 + "●", style="green")
                  lines[v_bot] = Text(" " * 24 + "●", style="cyan")
             else:
                  lines[1] = Text(" " * 24 + "💥", style="bold red")
        else:
            lines[1] = Text(" " * 20 + "💥 CONFLICT", style="bold red")

    elif pull_type == "ff":
        # Fast Forward: Simple vertical append from Ref Box (Bottom) to Local (Top)
        v_idx = int(2 * (1.0 - progress)) # Fly UP from 2 to 0
        lines[v_idx] = Text(" " * 24 + "🢁", style="bold green")

    return Group(*lines)

def render(state, anim_data):
    """Produce one frame of the pull animation."""
    if "stage" not in anim_data:
        anim_data["stage"] = "fetching"
        anim_data["frame"] = 0
    
    pull_type = getattr(state, "pull_type", "normal")
    is_rebase = getattr(state, "is_rebase", False)
    if pull_type == "normal" and is_rebase:
        pull_type = "rebase"
    
    tracking_name = getattr(state, "tracking_branch", "origin/main")
    local_branch = getattr(state, "branch", "main")
    behind = getattr(state, "behind", 0)

    # ── Header ─────────────────────────────────────────────
    title_text = f"Pull ({'Rebase' if is_rebase else 'Merge'}): {local_branch}"
    title = Text(title_text, style="bold cyan", justify="center")
    subtitle = Text(f"Remote: {tracking_name}", style="magenta", justify="center")

    # ── Branches ──────────────────────────────────────────
    branches_table = Table.grid(padding=(0, 4), expand=True)
    branches_table.add_column(ratio=1)
    branches_table.add_column(ratio=1)

    # Show new commits as magenta nodes after integration is complete
    show_new = (anim_data["stage"] == "waiting" and pull_type != "collision")
    new_local_count = behind if show_new else 0

    local_col = Group(
        Text(f" [Local] {local_branch}:", style="bold green"),
        _build_commit_chain(3, "green", new_commits=new_local_count)
    )
    remote_col = Group(
        Text(f" [Tracking] {tracking_name}:", style="bold cyan"),
        _build_commit_chain(3, "cyan")
    )
    branches_table.add_row(local_col, remote_col)

    # ── Animation Body ─────────────────────────────────────
    # Determine step count based on speed
    speed = getattr(state, "speed", "normal")
    speed_map = {"fast": 10, "normal": 25, "slow": 45}
    total_steps = speed_map.get(speed, 25)
    
    # Integration (Stage 2) is now 2x faster than fetch
    int_steps = max(5, total_steps // 2)
    
    # Real-time conflict/error detection
    if state.runner and state.runner.output_lines:
        last_lines = " ".join(state.runner.output_lines[-5:]).upper()
        if any(kw in last_lines for kw in ["CONFLICT", "AUTOMATIC MERGE FAILED", "ABORTING", "ERROR:"]):
            state.pull_type = "collision"

    if pull_type == "up_to_date":
        body = Group("", draw_box(content_char="✔", style="green"), "", Align.center(Text("Already up to date", style="bold green")))
    elif pull_type == "error":
        body = Group("", draw_box(content_char="!", style="red"), "", Align.center(Text("No upstream tracked", style="bold red")))
    elif anim_data["stage"] == "fetching":
        fly_area = _build_fly_area(anim_data["frame"], total_steps)
        ref_box = draw_box()
        note = Text(f"Stage 1: Fetching {behind} commits to {tracking_name}...", style="yellow", justify="center")
        
        anim_data["frame"] += 1
        if anim_data["frame"] >= total_steps:
            anim_data["stage"] = "integrating"
            anim_data["frame"] = 0
            
        body = Group(fly_area, ref_box, "", Align.center(note))
        
    elif anim_data["stage"] == "integrating":
        int_area = _build_integration_area(anim_data["frame"], int_steps, pull_type)
        ref_box = draw_box(content_char="⚙", style="blue")
        note_str = "Stage 2: Integrating changes..."
        if pull_type == "merge": note_str = "Stage 2: Creating 3-way merge commit..."
        elif pull_type == "rebase": note_str = "Stage 2: Rebasing local changes..."
        elif pull_type == "ff": note_str = "Stage 2: Fast-forwarding local branch..."
        elif pull_type == "collision": note_str = "Stage 2: Integration FAILED (Conflict!)"
        
        note = Text(note_str, style="bold cyan" if pull_type != "collision" else "bold red", justify="center")
        
        anim_data["frame"] += 1
        if anim_data["frame"] >= int_steps:
             anim_data["stage"] = "waiting"
             anim_data["wait"] = 0
             
        body = Group(int_area, ref_box, "", Align.center(note))
        
    elif anim_data["stage"] == "waiting":
        status_char = "✔" if pull_type != "collision" else "✘"
        status_style = "green" if pull_type != "collision" else "red"
        ref_box = draw_box(content_char=status_char, style=status_style)
        
        msg = f"Pull complete: integrated {behind} new commit(s)." if pull_type != "collision" else "Pull failed: check command output below."
        msg1 = Text(msg, style=f"bold {status_style}", justify="center")
        msg2 = Text("Restarting...", style="dim italic", justify="center")
        
        body = Group("", ref_box, "", Align.center(msg1), Align.center(msg2))
        
        anim_data["wait"] += 1
        if anim_data["wait"] >= 30:
            anim_data["stage"] = "fetching"
            anim_data["frame"] = 0
    else:
        body = Group("")

    frame_group = Group(title, subtitle, "", branches_table, body)
    return Panel(frame_group, title="vgit pull", border_style="magenta")

def start(layout_pane, git_state):
    """Start the pull animation loop."""
    return start_animation(layout_pane, render, git_state)
