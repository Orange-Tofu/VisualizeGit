# animations/clone.py
import curses
from vgit.animations.base import start_animation
from vgit.core import ui_config as cfg

# Characters (keep them simple so terminals that don't support fancy glyphs still look ok)
COMMIT_CHAR = "●"
PACKET_CHAR = "←"       # flying packet; replace with "🢀" if you prefer unicode
CONNECT = "─"
FOLDER_ICON = "📁"
REPO_ICON = "📦"

def _draw_commit_line(win, y, x, n_commits, color_pair):
    """Draw a horizontal commit line starting at (y, x) with n_commits nodes."""
    try:
        for i in range(n_commits):
            cx = x + i * 4
            win.addstr(y, cx, COMMIT_CHAR, curses.color_pair(color_pair))
            if i < n_commits - 1:
                win.addstr(y, cx + 1, CONNECT * 2, curses.color_pair(color_pair))
    except Exception:
        pass  # window too small — ignore

def draw_box(win, y, x, height, width, color, symbols):
    """
    Draw a box and render 'symbols' list of (sy, sx, sym) inside it.
    (copied / compatible with fetch.py)
    """
    try:
        win.attron(curses.color_pair(color))
        win.addstr(y + 1, x, "┌" + "─" * (width - 2) + "┐")
        for i in range(2, height):
            win.addstr(y + i, x, "│" + " " * (width - 2) + "│")
        win.addstr(y + height, x, "└" + "─" * (width - 2) + "┘")

        for sy, sx, sym in symbols:
            try:
                win.addstr(y + sy, x + sx, sym)
            except Exception:
                pass
        win.attroff(curses.color_pair(color))
    except Exception:
        pass

def draw_progress_bar(win, y, x, width, pct, color_pair):
    """Draw a simple progress bar like [====    ] XX% at (y,x)."""
    try:
        inner = max(0, width - 2)
        filled = int(inner * max(0.0, min(1.0, pct / 100.0)))
        bar = "[" + "=" * filled + " " * (inner - filled) + "]"
        win.addstr(y, x, bar, curses.color_pair(color_pair) | curses.A_BOLD)
        pct_text = f" {int(pct)}% "
        win.addstr(y, x + width + 1, pct_text)
    except Exception:
        pass

def render(window, state):
    # --- colors (same pairs as fetch.py, use cfg.STATUS_COLORS mapping) ---
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)

    # --- init internal animation state ---
    if not hasattr(state, "_clone_stage"):
        state._clone_stage = "connecting"
    if not hasattr(state, "_clone_frame"):
        state._clone_frame = 0

    # User-supplied or default values
    total_files = int(getattr(state, "total_files", len(getattr(state, "files", [])) or 12))
    file_list = list(getattr(state, "files", []))
    if len(file_list) < total_files:
        # generate placeholder names if not enough supplied
        for i in range(len(file_list), total_files):
            file_list.append(f"file_{i + 1}.py")

    # positions (use same config keys as fetch.py)
    left_x = cfg.STATUS_X_POSITIONS.get("untracked", 5)
    right_x = cfg.STATUS_X_POSITIONS.get("committed", 65)
    line_y = cfg.ROW_Y + 2

    h, w = window.getmaxyx()
    window.clear()
    window.box()

    # Title / subtitle
    repo_name = getattr(state, "repo_name", None) or getattr(state, "remote_url", "remote-repo")
    title = f"Clone: {repo_name}"
    try:
        window.addstr(1, max(2, (w - len(title)) // 2), title,
                      curses.color_pair(cfg.STATUS_COLORS.get("magenta", 1)) | curses.A_BOLD)
    except Exception:
        pass

    # Draw remote repo (right) and local folder (left)
    base_remote_nodes = 3
    _draw_commit_line(window, line_y + 1, right_x + 5, base_remote_nodes, cfg.STATUS_COLORS.get("cyan", 5))
    try:
        window.addstr(line_y - 1, right_x, f"[Remote] {repo_name}:", curses.color_pair(cfg.STATUS_COLORS.get("cyan", 5)))
    except Exception:
        pass

    LOCAL_NODES = 1
    _draw_commit_line(window, line_y + 1, left_x + 5, LOCAL_NODES, cfg.STATUS_COLORS.get("green", 3))
    try:
        window.addstr(line_y - 1, left_x, "[Local]:", curses.color_pair(cfg.STATUS_COLORS.get("green", 3)))
    except Exception:
        pass

    # Draw local box (contents will be populated as files are "cloned")
    local_box_y = line_y + 2
    local_box_x = left_x + 8
    local_box_h = 6
    local_box_w = 20

    # remote repo small box
    remote_box_y = line_y + 2
    remote_box_x = right_x + 4
    remote_box_h = 4
    remote_box_w = 22

    draw_box(window, remote_box_y, remote_box_x, remote_box_h, remote_box_w,
             cfg.STATUS_COLORS.get("cyan", 5),
             [(1, 2, REPO_ICON)])

    draw_box(window, local_box_y, local_box_x, local_box_h, local_box_w,
             cfg.STATUS_COLORS.get("yellow", 4),
             [(1, 2, FOLDER_ICON)])

    # --- Animation stages ---
    if state._clone_stage == "connecting":
        spinner = ["|", "/", "-", "\\"]
        spin_char = spinner[state._clone_frame % len(spinner)]
        note = f"Connecting to {repo_name}... {spin_char}"
        try:
            window.addstr(line_y + 8, max(4, (w - len(note)) // 2), note,
                          curses.color_pair(cfg.STATUS_COLORS.get("magenta", 1)))
        except Exception:
            pass

        # After a few frames move to cloning
        if state._clone_frame >= 6:
            state._clone_stage = "cloning"
            state._clone_frame = 0

    elif state._clone_stage == "cloning":
        # parameters
        frames_per_file = 6
        total_steps = frames_per_file * total_files

        # derive current progress from frame counter
        current_file_index = min(total_files - 1, state._clone_frame // frames_per_file)
        frame_in_file = state._clone_frame % frames_per_file
        cloned_count = min(total_files, state._clone_frame // frames_per_file)

        # positions for flying packet
        remote_head_x = remote_box_x - 1  # just left of remote box
        remote_head_y = remote_box_y + 1
        box_center_x = local_box_x + (local_box_w // 2)
        box_center_y = local_box_y + (local_box_h // 2)

        # smooth interpolation from remote -> local for the current file
        try:
            fly_x = int(remote_head_x - (remote_head_x - box_center_x) * (frame_in_file / max(1, frames_per_file)))
            fly_y = int(remote_head_y - (remote_head_y - box_center_y) * (frame_in_file / max(1, frames_per_file)))
            window.addstr(fly_y, fly_x, PACKET_CHAR,
                          curses.color_pair(cfg.STATUS_COLORS.get("red", 2)) | curses.A_BOLD)
        except Exception:
            pass

        # Render files that have been cloned inside local box
        try:
            max_files_display = local_box_h - 2
            for i in range(min(cloned_count, max_files_display)):
                fname = file_list[i][:local_box_w - 4]
                win_y = local_box_y + 1 + i
                win_x = local_box_x + 2
                window.addstr(win_y, win_x, fname)
        except Exception:
            pass

        # Progress bar at bottom
        progress_pct = (state._clone_frame / total_steps) * 100 if total_steps > 0 else 100
        try:
            draw_progress_bar(window, line_y + 8, max(4, (w - 40) // 2), 30, progress_pct, cfg.STATUS_COLORS.get("yellow", 4))
            status_text = f"Cloning objects: {cloned_count}/{total_files}"
            window.addstr(line_y + 9, max(4, (w - len(status_text)) // 2), status_text)
        except Exception:
            pass

        # Advance frame; when done switch to unpacking
        state._clone_frame += 1
        if state._clone_frame >= total_steps:
            state._clone_stage = "unpacking"
            state._clone_frame = 0
            # record final counts on state in case caller needs them
            state._clone_finished_files = total_files
            return window.refresh()

        # return early because we already updated frame
        window.refresh()
        return

    elif state._clone_stage == "unpacking":
        # small unpacking animation
        unpack_frames = 30
        pct = min(100, int((state._clone_frame / unpack_frames) * 100))
        try:
            note = "Unpacking objects..."
            window.addstr(line_y + 7, max(4, (w - len(note)) // 2), note,
                          curses.color_pair(cfg.STATUS_COLORS.get("magenta", 1)))
            draw_progress_bar(window, line_y + 8, max(4, (w - 40) // 2), 30, pct, cfg.STATUS_COLORS.get("magenta", 1))
        except Exception:
            pass

        state._clone_frame += 1
        if state._clone_frame >= unpack_frames:
            state._clone_stage = "done"
            state._clone_frame = 0

    elif state._clone_stage == "done":
        fetched = getattr(state, "_clone_finished_files", total_files)
        msg1 = f"Clone complete: {fetched} file(s) fetched."
        msg2 = "You can now `cd` into the repository and start working."
        try:
            center_y = h // 2
            center_x = w // 2
            window.addstr(center_y, max(0, center_x - len(msg1) // 2), msg1,
                          curses.color_pair(cfg.STATUS_COLORS.get("green", 3)) | curses.A_BOLD)
            window.addstr(center_y + 1, max(0, center_x - len(msg2) // 2), msg2)
        except Exception:
            pass

    # default frame increment for stages other than cloning (which increments inside)
    state._clone_frame += 1
    window.refresh()


def start(window, git_state):
    """
    Start the clone animation loop. Returns (stop_event, thread) as per animations.base.start_animation.
    """
    return start_animation(window, render, git_state)
