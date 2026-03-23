# animations/commit.py
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

COMMIT_CHAR = "◉"

def _render_existing_commits(state):
    """Return two Text objects (lines) showing shared history."""
    # Use the recorded base history so the history chain doesn't shift
    h_list = getattr(state, "base_hashes", [])
    m_list = getattr(state, "base_messages", [])
    
    # If not recorded (unlikely), fallback once
    if not h_list:
        h_list = state.commit_hashes
        m_list = state.commit_messages
    
    commits = h_list[-3:]
    messages = m_list[-3:]
    
    l1 = Text()
    l2 = Text()
    
    # Arrows now 3-segmented as requested
    arrow_part = " ──▶──▶──▶ "
    bubble_part = f" {COMMIT_CHAR} "
    
    for i, (chash, msg) in enumerate(zip(commits, messages)):
        hash_txt = f"({chash[:8]})" if chash else "(--------)"
        msg_txt = f'"{msg[:12]}"' if msg else '""'
        
        # Line 1:  ◉  (hash) 
        l1.append(bubble_part, style="green")
        l1.append(hash_txt, style="yellow")
        
        # Line 2:     "msg"
        # Directly below the hash start skip width of bubble
        l2.append(" " * len(bubble_part))
        l2.append(msg_txt, style="yellow")
        
        # SYNC: Pad both lines to match the wider one (likely message)
        max_w = max(len(l1), len(l2))
        l1.append(" " * (max_w - len(l1)))
        l2.append(" " * (max_w - len(l2)))
        
        # Arrow only BETWEEN commits to ensure dots are properly connected
        if i < len(commits) - 1:
            l1.append(arrow_part, style="green")
            l2.append(" " * len(arrow_part))
            
    return l1, l2

def render_commit_m(state, anim_data):
    if "frame" not in anim_data:
        anim_data["frame"] = 0

    frame = anim_data["frame"]
    l1, l2 = _render_existing_commits(state)
    
    arrow_part = " ──▶──▶──▶ "
    bubble_part = f" {COMMIT_CHAR} "
    
    # animation
    max_frames = 20
    wait_frames = 25
    
    restarting_note = ""
    if frame < max_frames:
        fly_spaces = " " * (max_frames - frame) * 2
        # Connect existing chain to flying commit
        if len(l1) > 0:
            l1.append(arrow_part, style="cyan")
            l2.append(" " * len(arrow_part))
        
        l1.append(fly_spaces + bubble_part, style="cyan")
        l2.append(" " * (len(fly_spaces) + len(bubble_part)))
        
        note = f"Branch: {state.branch} – Adding new commit..."
    elif frame < max_frames + wait_frames:
        if len(l1) > 0:
            l1.append(arrow_part, style="cyan")
            l2.append(" " * len(arrow_part))
            
        l1.append(bubble_part, style="cyan")
        
        # Better newness detection: Has the latest hash changed relative to base?
        base_h = state.base_hashes[-1] if state.base_hashes else None
        curr_h = state.commit_hashes[-1] if state.commit_hashes else None
        
        # If we had no history and now have one, or if the last hash changed
        has_new = curr_h and (curr_h != base_h)
        
        if has_new:
            hash_txt = f"({curr_h[:8]})"
            note = "New commit added!"
        else:
            hash_txt = "(........)"
            if getattr(state, "commit_type", "") == "failed":
                note = "Commit FAILED! (nothing staged?)"
            else:
                note = "Finalizing commit..."
        
        l1.append(hash_txt, style="yellow")
        
        msg_val = state.commit_message[:12] if hasattr(state, "commit_message") and state.commit_message else "New"
        msg_txt = f'"{msg_val}"'
        
        # Align with hash start skip width of bubble
        l2.append(" " * len(bubble_part))
        l2.append(msg_txt, style="yellow")
        
        # SYNC finalized commit
        max_w = max(len(l1), len(l2))
        l1.append(" " * (max_w - len(l1)))
        l2.append(" " * (max_w - len(l2)))
        
        restarting_note = "Restarting animation..."
    else:
        # restart
        anim_data["frame"] = 0
        return render_commit_m(state, anim_data)
        
    head_text = Text("\nHEAD ↓\n", style="magenta bold")
    
    anim_data["frame"] += 1

    return Group(
        head_text,
        l1,
        l2,
        "",
        Align.center(Text(note, style="yellow")),
        "",
        Align.center(Text(restarting_note, style="dim italic"))
    )

def render_commit_amend(state, anim_data):
    if "frame" not in anim_data:
        anim_data["frame"] = 0

    frame = anim_data["frame"]
    l1, l2 = _render_existing_commits(state)
    
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
        l1,
        l2,
        staging,
        "",
        Align.center(note),
        "",
        Align.center(Text(restarting_note, style="dim italic"))
    )


def render(state, anim_data):
    ctype = getattr(state, "commit_type", "commit_m")
    if ctype in ("commit_m", "failed"):
        content = render_commit_m(state, anim_data)
    elif ctype in ("amend_no_edit", "amend_with_m"):
        content = render_commit_amend(state, anim_data)
    else:
        content = Text("Unsupported commit animation")
        
    return Panel(content, title="vgit commit", border_style="blue")

def start(layout_pane, git_state):
    return start_animation(layout_pane, render, git_state)
