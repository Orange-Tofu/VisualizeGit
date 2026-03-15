# animations/fetch.py
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

COMMIT_CHAR = "●"
FLYING_COMMIT_CHAR = "🢀"
CONNECT = "─"

def _draw_commit_line(n_commits, color):
    t = Text(style=color)
    for i in range(n_commits):
        t.append(COMMIT_CHAR)
        if i < n_commits - 1:
            t.append(" " + CONNECT * 2 + " ")
    return t

def render(state):
    if not hasattr(state, "_fetch_stage"):
        state._fetch_stage = "fetching"
    if not hasattr(state, "_fetch_frame"):
        state._fetch_frame = 0

    title = f"Fetch: {state.branch}"
    tracking_name = getattr(state, "tracking_branch", None)
    subtitle = f"Remote-tracking: {tracking_name}" if tracking_name else "No remote tracking branch"

    local_line = _draw_commit_line(4, "green")
    remote_line = _draw_commit_line(3, "cyan")

    local_label = Text(f"[Local] ({state.branch}):", style="green")
    remote_label = Text(f"[Remote] {tracking_name}:" if tracking_name else "[Remote]:", style="cyan")

    total_steps = 10
    step = state._fetch_frame % total_steps
    distance = 20
    fly_pos = int(distance * (total_steps - step) / total_steps)
    fly_line = Text(" " * fly_pos + FLYING_COMMIT_CHAR, style="red bold")

    if state._fetch_stage == "fetching":
        anim_note = Text("Fetching commits... remote data moving to Local Ref", style="yellow")
        state._fetch_frame += 1
        if step == total_steps - 1:
            state._fetch_stage = "done"
    else:
        fetched = int(getattr(state, "behind", 0))
        msg1 = f"Fetched {fetched} new commit(s) for this branch." if fetched > 0 else "No new commits fetched for this branch."
        msg2 = "Commits fetched to remote-tracking refs, not merged into local branches."
        fly_line = Text("")
        anim_note = Text(msg1 + "\n" + msg2, style="bold green" if fetched > 0 else "magenta", justify="center")

    group = Group(
        Text(title, style="bold magenta", justify="center"),
        Text(subtitle, style="magenta", justify="center"),
        "",
        local_label,
        local_line,
        "",
        remote_label,
        remote_line,
        "",
        Text("[Local Ref Box]", style="yellow"),
        fly_line,
        "",
        Align.center(anim_note)
    )

    return Panel(group, title="vgit fetch", border_style="blue")

def start(layout_pane, git_state):
    return start_animation(layout_pane, render, git_state)
