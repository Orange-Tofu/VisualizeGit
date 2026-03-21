# animations/fetch.py
"""Fetch animation — visualizes commits moving from remote to local ref."""
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

COMMIT_CHAR = "●"
FLYING_COMMIT_CHAR = "🢀"
CONNECT = "──"


def _build_commit_chain(n_commits, style):
    """Return a Text object showing n commit nodes linked by arrows."""
    chain = Text()
    for i in range(n_commits):
        chain.append(f" {COMMIT_CHAR} ", style=style)
        if i < n_commits - 1:
            chain.append(CONNECT, style=style)
    return chain


def _build_local_ref_box(content_char="•", style="yellow", left_pad=18):
    """Return a multi-line Text representing the local-ref storage box, offset to align under local branch."""
    pad = " " * left_pad
    box = Text()
    box.append(f"{pad}┌────────────┐\n", style=style)
    box.append(f"{pad}│ Local Ref  │\n", style=style)
    box.append(f"{pad}│     {content_char}      │\n", style=style)
    box.append(f"{pad}└────────────┘", style=style)
    return box


def _build_fly_area(frame, total_steps, start_x=85, end_x=24, vertical_rows=5):
    """Build a multi-line area with the flying commit at interpolated (x, y).

    Starts at `start_x` (remote branch center) and travels to `end_x` (box center).
    """
    step = frame % total_steps
    progress = min(1.0, step / max(total_steps - 1, 1))
        
    # Horizontal: start_x → end_x
    h_pos = int(start_x - (start_x - end_x) * progress)
    # Vertical: row 0 (top) → row vertical_rows-1 (bottom, at box)
    v_row = int((vertical_rows - 1) * progress)

    lines = []
    for row in range(vertical_rows):
        if row == v_row:
            line = Text()
            line.append(" " * h_pos)
            line.append(FLYING_COMMIT_CHAR, style="red bold")
            lines.append(line)
        else:
            lines.append(Text(""))
    return Group(*lines)


def render(state, anim_data):
    """Produce one frame of the fetch animation as a rich renderable."""
    if "stage" not in anim_data:
        anim_data["stage"] = "fetching"
    if "frame" not in anim_data:
        anim_data["frame"] = 0

    tracking_name = getattr(state, "tracking_branch", None)

    # ── header ──────────────────────────────────────────────
    title = Text(f"Fetch: {state.branch}", style="bold magenta", justify="center")
    subtitle_txt = (
        f"Remote-tracking: {tracking_name}" if tracking_name else "No remote tracking branch"
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

    remote_label_txt = (
        f"      [Remote] {tracking_name}:" if tracking_name else "      [Remote]:"
    )
    remote_label = Text(remote_label_txt, style="bold cyan")
    remote_chain = _build_commit_chain(3, "cyan")
    remote_chain.pad_left(6)
    remote_col = Group(remote_label, remote_chain)

    branches_table.add_row(local_col, remote_col)

    # ── animation body ──────────────────────────────────────
    total_steps = 30

    if anim_data["stage"] == "fetching":
        fly_area = _build_fly_area(
            anim_data["frame"], 
            total_steps=total_steps,
            start_x=85, 
            end_x=24, 
            vertical_rows=5
        )
        ref_box = _build_local_ref_box()
        note = Text(
            "Fetching commits… remote data moving to Local Ref",
            style="yellow",
            justify="center",
        )

        anim_data["frame"] += 1
        if anim_data["frame"] >= total_steps:
            anim_data["stage"] = "waiting"
            anim_data["wait"] = 0

        # branches (top) → fly area (arrow descends) → box (bottom)
        body = Group(
            fly_area,
            ref_box,
            "",
            Align.center(note),
        )
    elif anim_data["stage"] == "waiting":
        # Visuals of 'done' state but with a delay before restart
        fetched = int(getattr(state, "behind", 0))
        ref_box = _build_local_ref_box(content_char="✔", style="green")
        
        msg = f"Fetched {fetched} new commit(s)." if fetched > 0 else "No new commits fetched."
        msg1 = Text(msg, style="bold green", justify="center")
        msg2 = Text("Restarting animation...", style="dim italic", justify="center")

        body = Group("", ref_box, "", Align.center(msg1), Align.center(msg2))
        
        anim_data["wait"] += 1
        if anim_data["wait"] >= 25: # ~2.5 seconds at 10fps
            anim_data["stage"] = "fetching"
            anim_data["frame"] = 0
    else:
        # Fallback
        body = Group("")

    # ── assemble ────────────────────────────────────────────
    frame_group = Group(
        title,
        subtitle,
        "",
        branches_table,
        body,
    )

    return Panel(frame_group, title="vgit fetch", border_style="blue")


def start(layout_pane, git_state):
    """Start the fetch animation loop."""
    return start_animation(layout_pane, render, git_state)
