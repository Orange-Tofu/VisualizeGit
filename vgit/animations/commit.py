# animations/commit.py
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

COMMIT_CHAR = "◉"

def _render_existing_commits(state):
    commits = state.commit_hashes[-3:] if hasattr(state, "commit_hashes") else []
    messages = state.commit_messages[-3:] if hasattr(state, "commit_messages") else [f"Commit{i+1}" for i in range(len(commits))]
    
    t = Text()
    for i, (chash, msg) in enumerate(zip(commits, messages)):
        hash_txt = "#→ " + chash[:4] if chash else "----"
        t.append(f" {COMMIT_CHAR} ", style="green")
        t.append(f" ({hash_txt}) ", style="yellow")
        t.append(f'"{msg[:8]}"', style="yellow")
        if i < len(commits) - 1:
            t.append(" ──▶──▶ ", style="green")
    return t

def render_commit_m(state, anim_data):
    if "frame" not in anim_data:
        anim_data["frame"] = 0

    frame = anim_data["frame"]
    commits_text = _render_existing_commits(state)
    
    # animation
    max_frames = 20
    wait_frames = 25
    
    restarting_note = ""
    if frame < max_frames:
        fly_spaces = " " * (max_frames - frame) * 2
        commits_text.append(fly_spaces + f" ──▶──▶  {COMMIT_CHAR} ", style="cyan")
        note = f"Branch: {state.branch} – Adding new commit..."
    elif frame < max_frames + wait_frames:
        commits_text.append(f" ──▶──▶  {COMMIT_CHAR} ", style="cyan")
        msg = state.commit_message[:8] if hasattr(state, "commit_message") and state.commit_message else "New"
        commits_text.append(f' "{msg}"', style="yellow")
        note = "New commit added!"
        restarting_note = "Restarting animation..."
    else:
        # restart
        anim_data["frame"] = 0
        return render_commit_m(state, anim_data)
        
    head_text = Text("\nHEAD ↓\n", style="magenta bold")
    
    anim_data["frame"] += 1

    return Group(
        head_text,
        commits_text,
        "",
        Align.center(Text(note, style="yellow")),
        "",
        Align.center(Text(restarting_note, style="dim italic"))
    )

def render_commit_amend(state, anim_data):
    if "frame" not in anim_data:
        anim_data["frame"] = 0

    frame = anim_data["frame"]
    commits_text = _render_existing_commits(state)
    
    max_frames = 25
    wait_frames = 20
    
    restarting_note = ""
    if frame <= 10:
        note = Text("Files moved to staging area...", style="yellow")
    elif frame < max_frames:
        note = Text("Creating replacement commit...", style="yellow")
    elif frame < max_frames + wait_frames:
        note = Text("Replaced old commit with amended commit!", style="green")
        restarting_note = "Restarting animation..."
    else:
        anim_data["frame"] = 0
        return render_commit_amend(state, anim_data)
        
    staging = Text("\n[STAGING AREA]\n• Existing changes", style="red")
    
    anim_data["frame"] += 1
    
    return Group(
        commits_text,
        staging,
        "",
        Align.center(note),
        "",
        Align.center(Text(restarting_note, style="dim italic"))
    )


def render(state, anim_data):
    ctype = getattr(state, "commit_type", "commit_m")
    if ctype == "commit_m":
        content = render_commit_m(state, anim_data)
    elif ctype in ("amend_no_edit", "amend_with_m"):
        content = render_commit_amend(state, anim_data)
    else:
        content = Text("Unsupported commit animation")
        
    return Panel(content, title="vgit commit", border_style="blue")

def start(layout_pane, git_state):
    return start_animation(layout_pane, render, git_state)
