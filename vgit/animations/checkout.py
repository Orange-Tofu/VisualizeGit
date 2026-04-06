# animations/checkout.py
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.console import Group
from vgit.animations.base import start_animation

COMMIT_CHAR = "◉"
BRANCH_ICON = " "
HEAD_ICON = "HEAD"
ARROW = "──▶"

def _render_commit_chain(hashes, messages, color="green"):
    """Render a horizontal chain of commits."""
    l1 = Text()
    l2 = Text()
    
    bubble_part = f" {COMMIT_CHAR} "
    arrow_part = f" {ARROW} "
    
    for i, (chash, msg) in enumerate(zip(hashes, messages)):
        hash_txt = f"({chash[:8]})"
        msg_txt = f'"{msg[:10]}"'
        
        l1.append(bubble_part, style=color)
        l1.append(hash_txt, style="yellow")
        
        l2.append(" " * len(bubble_part))
        l2.append(msg_txt, style="yellow")
        
        max_w = max(len(l1), len(l2))
        l1.append(" " * (max_w - len(l1)))
        l2.append(" " * (max_w - len(l2)))
        
        if i < len(hashes) - 1:
            l1.append(arrow_part, style=color)
            l2.append(" " * len(arrow_part))
            
    return l1, l2

def _render_delete_animation(state, anim_data):
    frame = anim_data.get("frame", 0)
    branch_name = state.delete_branch_name or "branch"
    hashes = getattr(state, "base_hashes", [])
    messages = getattr(state, "base_messages", [])
    
    # Render the branch as a commit chain
    # Deleting effect: Shake and then fade/red
    colors = ["red", "bold red", "white", "bold red"]
    color = colors[frame % len(colors)]
    
    if frame < 20:
        l1, l2 = _render_commit_chain(hashes, messages, color=color)
        l1.append(f" [{branch_name}]", style=f"bold {color}")
        note = f"Deleting branch {branch_name}..."
        restarting_note = Text("")
    else:
        # Fading out/broken chain
        l1 = Text(" " * 5 + "X" * 10, style="dim red")
        l2 = Text(" " * 5 + "BRANCH REMOVED", style="dim strike red")
        note = f"Branch {branch_name} deleted."
        restarting_note = Text("Restarting animation...", style="dim italic")
        
    # Repeat handling
    anim_data["frame"] += 1
    if anim_data["frame"] > 50:
        anim_data["frame"] = 0
        
    return Group(
        "",
        Align.center(l1),
        Align.center(l2)
    ), Text(note, style="bold red"), restarting_note

def render(state, anim_data):
    """Render the checkout/switch/create animation."""
    if "frame" not in anim_data:
        anim_data["frame"] = 0
    if "stage" not in anim_data:
        anim_data["stage"] = "init"
        
    frame = anim_data["frame"]
    checkout_type = getattr(state, "checkout_type", "branch")
    
    if checkout_type == "delete_branch":
        content, note, restarting_note = _render_delete_animation(state, anim_data)
        return Panel(
            Group(
                "",
                Align.center(content),
                "",
                Align.center(note),
                "",
                Align.center(restarting_note)
            ),
            title=f"vgit branch -d {state.delete_branch_name}",
            border_style="red"
        )

    # Branch switching/creation logic
    current_branch = state.branch
    target_branch = state.target_branch or "???"
    is_new = state.is_new_branch
    hashes = getattr(state, "base_hashes", [])
    messages = getattr(state, "base_messages", [])
    status = getattr(state, "checkout_status", "running")
    
    # Stages: 'init', 'branching', 'moving', 'done'
    if anim_data["stage"] == "init":
        if frame > 5:
            anim_data["stage"] = "branching" if is_new else "moving"
            anim_data["frame"] = 0
    
    anim_data["frame"] += 1
    
    # Render Base Branch (e.g. main)
    base_l1, base_l2 = _render_commit_chain(hashes, messages, color="green")
    base_branch_tag = Text(f" [{current_branch}]", style="bold green")
    base_l1.append(base_branch_tag)
    
    content = Group()
    
    # Base note instead of 'Preparing...'
    if is_new:
        note = f"Branching off from {current_branch}..."
    else:
        note = f"Switching to {target_branch}..."

    total_steps = 20
    progress = 0
    restarting_note = Text("")
    
    if is_new:
        fork_x = base_l1.plain.rfind(COMMIT_CHAR)
        if fork_x == -1:
            fork_x = 0
            
        head_x = len(base_l1.plain) + 2

        if anim_data["stage"] == "branching":
            progress = min(1.0, anim_data["frame"] / total_steps)
            if progress >= 1.0:
                if status == "failed":
                    anim_data["stage"] = "failed"
                else:
                    anim_data["stage"] = "moving"
                anim_data["frame"] = 0
            
            num_verts = int(progress * 3)
            lines = [base_l1.copy(), base_l2.copy()]
            for _ in range(num_verts):
                lines.append(Text(" " * fork_x + "│", style="bold yellow"))
            
            lines[0].append("  <- HEAD", style="bold cyan")
            
            content = Group(*lines)
            note = f"Branching off from {current_branch}..."
            
        elif anim_data["stage"] == "moving":
            progress = min(1.0, anim_data["frame"] / total_steps)
            if progress >= 1.0:
                anim_data["stage"] = "done"
                anim_data["wait"] = 0
            
            lines = [base_l1.copy(), base_l2.copy()]
            for _ in range(3):
                lines.append(Text(" " * fork_x + "│", style="bold yellow"))
                
            new_l1 = Text(" " * fork_x)
            new_l1.append(f"{COMMIT_CHAR} ", style="bold yellow")
            if hashes:
                new_l1.append(f"({hashes[-1][:8]})", style="yellow")
            new_l1.append(f" {BRANCH_ICON}{target_branch}", style="bold yellow")
            lines.append(new_l1)
            
            if hashes and messages:
                new_l2 = Text(" " * (fork_x + 2))
                new_l2.append(f'"{messages[-1][:10]}"', style="yellow")
                lines.append(new_l2)
            
            y_pos = int(progress * 5) # 0 to 5
            
            for i, line in enumerate(lines):
                if i == y_pos:
                    pad = max(1, head_x - len(line.plain))
                    line.append(" " * pad + "<- HEAD", style="bold cyan")
                    
            content = Group(*lines)
            note = f"Moving HEAD to {target_branch}..."
            
        elif anim_data["stage"] == "done":
            lines = [base_l1.copy(), base_l2.copy()]
            for _ in range(3):
                lines.append(Text(" " * fork_x + "│", style="bold green"))
                
            new_l1 = Text(" " * fork_x)
            new_l1.append(f"{COMMIT_CHAR} ", style="bold green")
            if hashes:
                new_l1.append(f"({hashes[-1][:8]})", style="yellow")
            new_l1.append(f" {BRANCH_ICON}{target_branch}", style="bold green")
            
            pad = max(1, head_x - len(new_l1.plain))
            new_l1.append(" " * pad + "<- HEAD", style="bold cyan")
            lines.append(new_l1)
            
            if hashes and messages:
                new_l2 = Text(" " * (fork_x + 2))
                new_l2.append(f'"{messages[-1][:10]}"', style="yellow")
                lines.append(new_l2)
                
            content = Group(*lines)
            note = f"Switched to {target_branch}"
            restarting_note = Text("Restarting animation...", style="dim italic")
            
            anim_data["wait"] += 1
            if anim_data["wait"] > 30:
                anim_data["stage"] = "init"
                anim_data["frame"] = 0

        elif anim_data["stage"] == "failed":
            lines = [base_l1.copy(), base_l2.copy()]
            for _ in range(2):
                lines.append(Text(" " * fork_x + "│", style="bold red"))
            lines.append(Text(" " * fork_x + "X", style="bold red"))
            
            lines[0].append("  <- HEAD", style="bold cyan")
            
            content = Group(*lines)
            note = Text(f"Failed to create branch '{target_branch}'!", style="bold red")
            restarting_note = Text("Restarting animation...", style="dim italic")
            
            anim_data["wait"] = anim_data.get("wait", 0) + 1
            if anim_data["wait"] > 25:
                 anim_data["stage"] = "init"
                 anim_data["frame"] = 0
                 anim_data["wait"] = 0

    else:
        # Simple Switch
        if anim_data["stage"] == "moving":
            progress = min(1.0, anim_data["frame"] / total_steps)
            if progress >= 1.0:
                if status == "failed":
                    anim_data["stage"] = "failed"
                else:
                    anim_data["stage"] = "done"
                anim_data["frame"] = 0
        
        if anim_data["stage"] == "done":
            progress = 1.0
            restarting_note = Text("Restarting animation...", style="dim italic")
            note = f"Switched to {target_branch}"
            anim_data["wait"] = anim_data.get("wait", 0) + 1
            if anim_data["wait"] > 30:
                anim_data["stage"] = "init"
                anim_data["frame"] = 0
                anim_data["wait"] = 0
                
        elif anim_data["stage"] == "failed":
            progress = 0.0
            restarting_note = Text("Restarting animation...", style="dim italic")
            note = Text(f"Switch to '{target_branch}' failed!", style="bold red")
            anim_data["wait"] = anim_data.get("wait", 0) + 1
            if anim_data["wait"] > 25:
                anim_data["stage"] = "init"
                anim_data["frame"] = 0
                anim_data["wait"] = 0

        target_l1, target_l2 = _render_commit_chain(hashes, messages, color="blue")
        target_l1.append(f" [{target_branch}]", style="bold yellow" if progress < 1.0 else "bold green")
        
        head = Text(" " * (len(base_l1) - len(base_branch_tag)) + "  <- HEAD", style="bold cyan")
        
        if anim_data.get("stage") == "failed":
            content = Group(target_l1, target_l2, "", base_l1, base_l2)
        else:
            if progress < 0.5:
                content = Group(target_l1, target_l2, "", head, base_l1, base_l2)
            else:
                target_l1.append("  <- HEAD", style="bold cyan")
                content = Group(target_l1, target_l2, "", base_l1, base_l2)

    return Panel(
        Group(
            "",
            Align.center(content),
            "",
            Align.center(note if isinstance(note, Text) else Text(str(note), style="yellow")),
            "",
            Align.center(restarting_note)
        ),
        title=f"vgit {checkout_type}",
        border_style="blue"
    )

def start(layout_pane, git_state):
    """Initialize and start the checkout animation."""
    return start_animation(layout_pane, render, git_state)
