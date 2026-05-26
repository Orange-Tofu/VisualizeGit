# animations/merge.py
"""
Merge animation — visualizes fast-forward, 3-way merges, and conflicts with detailed commits.
Uses a continuous loop pattern with status messages for the user.
"""
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

COMMIT_CHAR = "◉"
CONNECT = "──"
ARROW = "──▶"
MERGE_CHAR = "◆"

def _render_branch_chain(hashes, messages, style, max_commits=3, include_new_indices=None, new_commits_progress=0.0):
    """
    Renders a branch's commit chain showing actual commit hashes and messages.
    
    Why: Shows exact commit nodes (hashes & messages) to make the TUI clear
    and educational, rather than just using generic dots. Supports sliding/flying logic.
    """
    l1 = Text()
    l2 = Text()
    arrow_part = f" {ARROW} "
    bubble_part = f" {COMMIT_CHAR} "
    
    # Ensure there are always fallback lists if empty
    if not hashes:
        hashes = ["", "", ""]
        messages = ["", "", ""]
        
    commits = hashes[-max_commits:]
    msgs = messages[-max_commits:]
    
    # Calculate which nodes to draw
    for i, (chash, msg) in enumerate(zip(commits, msgs)):
        is_new = False
        if include_new_indices is not None:
            orig_idx = len(hashes) - len(commits) + i
            if orig_idx in include_new_indices:
                is_new = True
                
        # If it's a new commit (fast-forward) and integration hasn't finished,
        # we hide it from the active branch chain so it can "fly in" from below.
        if is_new and new_commits_progress < 1.0:
            continue
            
        hash_txt = f"({chash[:8]})" if chash else "(--------)"
        msg_txt = f'"{msg[:10]}"' if msg else '""'
        
        # Color new commits magenta to emphasize successful merge/FF
        curr_style = "bold magenta" if is_new else style
        l1.append(bubble_part, style=curr_style)
        l1.append(hash_txt, style="yellow")
        
        l2.append(" " * len(bubble_part))
        l2.append(msg_txt, style="yellow")
        
        # Sync line widths
        max_w = max(len(l1), len(l2))
        l1.append(" " * (max_w - len(l1)))
        l2.append(" " * (max_w - len(l2)))
        
        if i < len(commits) - 1:
            next_idx = len(hashes) - len(commits) + i + 1
            if include_new_indices is None or next_idx not in include_new_indices or new_commits_progress >= 1.0:
                l1.append(arrow_part, style=curr_style)
                l2.append(" " * len(arrow_part))
            
    return l1, l2

def _build_flying_ff_commits(new_hashes, new_messages, progress):
    """
    Renders the middle lines showing the new commits flying upwards from target to active branch.
    
    Why: Shows exactly which commits are being fast-forwarded from the target branch.
    """
    lines = [Text(""), Text(""), Text("")]
    if not new_hashes:
        return Group(*lines)
        
    # Vertical index goes from 2 (bottom/target) down to 0 (top/active)
    v_idx = int(2 * (1.0 - progress))
    
    l1 = Text()
    l2 = Text()
    arrow_part = f" {ARROW} "
    bubble_part = f" {COMMIT_CHAR} "
    
    for i, (chash, msg) in enumerate(zip(new_hashes, new_messages)):
        hash_txt = f"({chash[:8]})" if chash else "(--------)"
        msg_txt = f'"{msg[:10]}"' if msg else '""'
        
        l1.append(bubble_part, style="bold cyan")
        l1.append(hash_txt, style="yellow")
        
        l2.append(" " * len(bubble_part))
        l2.append(msg_txt, style="yellow")
        
        max_w = max(len(l1), len(l2))
        l1.append(" " * (max_w - len(l1)))
        l2.append(" " * (max_w - len(l2)))
        
        if i < len(new_hashes) - 1:
            l1.append(arrow_part, style="bold cyan")
            l2.append(" " * len(arrow_part))
            
    # Pad left to align with target branch commits
    l1.pad_left(20)
    l2.pad_left(20)
    
    if v_idx == 0:
        lines[0] = l1
        lines[1] = l2
    elif v_idx == 1:
        lines[1] = l1
        lines[2] = l2
    else:
        lines[2] = l1
        
    return Group(*lines)

def _build_3way_integration_area(state, frame, total_steps):
    """
    Renders two branch lines converging into a new merge commit node.
    
    Why: Visually demonstrates how a 3-way merge joins two distinct histories.
    """
    step = frame % total_steps
    progress = min(1.0, step / max(total_steps - 1, 1))
    
    lines = [Text(""), Text(""), Text(""), Text("")]
    
    # Merge commit details (dynamically resolved or fallback)
    merge_hash = state.commit_hashes[-1][:8] if state.commit_hashes else "--------"
    merge_msg = "Merge branch"
    
    center_x = 35
    if progress < 0.7:
        p_scaled = progress / 0.7
        x_pos = int(15 + (center_x - 15) * p_scaled)
        
        lines[0] = Text(" " * 15 + "╰" + "─" * (x_pos - 16) + "╮", style="green")
        lines[3] = Text(" " * 15 + "╭" + "─" * (x_pos - 16) + "╯", style="cyan")
        
        lines[1] = Text(" " * x_pos + COMMIT_CHAR, style="green")
        lines[2] = Text(" " * x_pos + COMMIT_CHAR, style="cyan")
    else:
        lines[0] = Text(" " * 15 + "╰" + "─" * (center_x - 16) + "╮", style="dim green")
        lines[3] = Text(" " * 15 + "╭" + "─" * (center_x - 16) + "╯", style="dim cyan")
        
        bubble = Text(" " * center_x + f" {MERGE_CHAR} ", style="bold magenta")
        bubble.append(f"({merge_hash})", style="yellow")
        lines[1] = bubble
        
        msg = Text(" " * (center_x + 5) + f'"{merge_msg}"', style="yellow")
        lines[2] = msg
        
    return Group(*lines)

def _build_conflict_integration_area(state, frame, total_steps):
    """
    Renders converging lines colliding head-on to represent a merge conflict.
    
    Why: Clearly visualizes that no merge commit could be successfully formed.
    """
    step = frame % total_steps
    progress = min(1.0, step / max(total_steps - 1, 1))
    
    lines = [Text(""), Text(""), Text(""), Text("")]
    center_x = 35
    
    if progress < 0.7:
        p_scaled = progress / 0.7
        x_pos = int(15 + (center_x - 15) * p_scaled)
        
        lines[0] = Text(" " * 15 + "╰" + "─" * (x_pos - 16) + "╮", style="green")
        lines[3] = Text(" " * 15 + "╭" + "─" * (x_pos - 16) + "╯", style="cyan")
        
        lines[1] = Text(" " * x_pos + COMMIT_CHAR, style="green")
        lines[2] = Text(" " * x_pos + COMMIT_CHAR, style="cyan")
    else:
        lines[0] = Text(" " * 15 + "╰" + "─" * (center_x - 16) + "╮", style="red")
        lines[3] = Text(" " * 15 + "╭" + "─" * (center_x - 16) + "╯", style="red")
        
        lines[1] = Text(" " * (center_x - 2) + "💥 CONFLICT", style="bold red")
        lines[2] = Text(" " * (center_x - 5) + "Automatic merge failed", style="bold red")
        
    return Group(*lines)

def render(state, anim_data):
    """
    Produces one frame of the merge TUI visualization.
    
    Why: Handles setup, side-by-side branch comparison, and stage transitions.
    """
    if "stage" not in anim_data:
        anim_data["stage"] = "evaluating"
        anim_data["frame"] = 0
    
    merge_type = getattr(state, "merge_type", "merge")
    target_branch = getattr(state, "target_branch", "target")
    local_branch = getattr(state, "branch", "main")
    behind = getattr(state, "behind", 0)

    # Resolve new commits for Fast-Forward animation
    active_hashes = getattr(state, "base_hashes", [])
    target_hashes = getattr(state, "target_hashes", [])
    target_msgs = getattr(state, "target_messages", [])
    
    new_indices = []
    new_hashes = []
    new_msgs = []
    for idx, thash in enumerate(target_hashes):
        if thash not in active_hashes:
            new_indices.append(idx)
            new_hashes.append(thash)
            new_msgs.append(target_msgs[idx])

    # ── Header ─────────────────────────────────────────────
    title_text = f"Merge: {target_branch} into {local_branch}"
    title = Text(title_text, style="bold cyan", justify="center")

    # ── Side-by-Side Commit Details ────────────────────────
    branches_table = Table.grid(padding=(0, 4), expand=True)
    branches_table.add_column(ratio=1)
    branches_table.add_column(ratio=1)

    # Active branch chain representation
    show_new = (anim_data["stage"] == "waiting" and merge_type != "collision" and merge_type != "error")
    new_commits_progress = 1.0 if show_new else 0.0
    
    # In fast-forward, active branch will eventually contain target branch commits
    active_display_hashes = target_hashes if merge_type == "ff" else active_hashes
    active_display_msgs = target_msgs if merge_type == "ff" else getattr(state, "base_messages", [])
    
    l_commits_1, l_commits_2 = _render_branch_chain(
        active_display_hashes, 
        active_display_msgs, 
        "green", 
        include_new_indices=new_indices if merge_type == "ff" else None,
        new_commits_progress=new_commits_progress
    )
    
    local_col = Group(
        Text(f" [Active] {local_branch}:", style="bold green"),
        l_commits_1,
        l_commits_2
    )

    # Target branch chain representation
    t_commits_1, t_commits_2 = _render_branch_chain(target_hashes, target_msgs, "cyan")
    target_col = Group(
        Text(f" [Target] {target_branch}:", style="bold cyan"),
        t_commits_1,
        t_commits_2
    )
    branches_table.add_row(local_col, target_col)

    # ── Animation Body ─────────────────────────────────────
    speed = getattr(state, "speed", "normal")
    speed_map = {"fast": 10, "normal": 25, "slow": 45}
    total_steps = speed_map.get(speed, 25)
    int_steps = max(5, total_steps // 2)
    
    # Real-time conflict/error detection by scraping output lines
    if state.runner and state.runner.output_lines:
        last_lines = " ".join(state.runner.output_lines[-5:]).upper()
        if any(kw in last_lines for kw in ["CONFLICT", "AUTOMATIC MERGE FAILED", "ABORTING", "ERROR:"]):
            state.merge_type = "collision"
            merge_type = "collision"

    if merge_type == "up_to_date":
        # Draw a beautiful success panel
        from vgit.animations.widgets import draw_box
        body = Group("", draw_box(content_char="✔", style="green"), "", Align.center(Text("Already up to date", style="bold green")))
    elif merge_type == "error":
        from vgit.animations.widgets import draw_box
        body = Group("", draw_box(content_char="!", style="red"), "", Align.center(Text("Merge failed: Invalid target branch", style="bold red")))
    elif anim_data["stage"] == "evaluating":
        from vgit.animations.widgets import draw_box
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"][anim_data["frame"] % 10]
        note = Text(f"{spinner} Finding common ancestor (merge-base)...", style="yellow", justify="center")
        ref_box = draw_box(content_char="?", style="yellow")
        
        anim_data["frame"] += 1
        if anim_data["frame"] >= 10:
            anim_data["stage"] = "integrating"
            anim_data["frame"] = 0
            
        body = Group("", ref_box, "", Align.center(note))
        
    elif anim_data["stage"] == "integrating":
        # Choose the right integration animation block
        if merge_type == "ff":
            progress = anim_data["frame"] / max(int_steps - 1, 1)
            int_area = _build_flying_ff_commits(new_hashes, new_msgs, progress)
            note_str = "Stage 2: Fast-forwarding active branch HEAD..."
        elif merge_type == "collision":
            int_area = _build_conflict_integration_area(state, anim_data["frame"], int_steps)
            note_str = "Stage 2: Merge FAILED (Conflict!)"
        else:
            int_area = _build_3way_integration_area(state, anim_data["frame"], int_steps)
            note_str = "Stage 2: Creating 3-way merge commit..."
        
        from vgit.animations.widgets import draw_box
        ref_box = draw_box(content_char="⚙", style="blue")
        note = Text(note_str, style="bold cyan" if merge_type != "collision" else "bold red", justify="center")
        
        anim_data["frame"] += 1
        if anim_data["frame"] >= int_steps:
             anim_data["stage"] = "waiting"
             anim_data["wait"] = 0
             
        body = Group(int_area, ref_box, "", Align.center(note))
        
    elif anim_data["stage"] == "waiting":
        from vgit.animations.widgets import draw_box
        status_char = "✔" if merge_type != "collision" else "✘"
        status_style = "green" if merge_type != "collision" else "red"
        ref_box = draw_box(content_char=status_char, style=status_style)
        
        if merge_type == "collision":
            msg = "Merge failed: Resolve conflicts manually."
        else:
            msg = f"Merge complete: integrated {behind} commit(s)."
            
        msg1 = Text(msg, style=f"bold {status_style}", justify="center")
        msg2 = Text("Restarting...", style="dim italic", justify="center")
        
        body = Group("", ref_box, "", Align.center(msg1), Align.center(msg2))
        
        anim_data["wait"] += 1
        if anim_data["wait"] >= 30:
            anim_data["stage"] = "evaluating"
            anim_data["frame"] = 0
    else:
        body = Group("")

    frame_group = Group(title, "", branches_table, body)
    return Panel(frame_group, title="vgit merge", border_style="magenta")

def start(layout_pane, git_state):
    """Start the merge animation loop."""
    return start_animation(layout_pane, render, git_state)
