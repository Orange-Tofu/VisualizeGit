# animations/fetch.py
import curses
from animations.base import start_animation
from core import ui_config as cfg

COMMIT_CHAR = "●"
FLYING_COMMIT_CHAR = "🢀"
CONNECT = "─"


def _draw_commit_line(win, y, x, n_commits, color_pair):
    """Draw a horizontal commit line starting at (y, x) with n_commits nodes."""
    try:
        for i in range(n_commits):
            cx = x + i * 4
            win.addstr(y, cx, COMMIT_CHAR, curses.color_pair(color_pair))
            if i < n_commits - 1:
                win.addstr(y, cx + 1, CONNECT * 2, curses.color_pair(color_pair))
    except Exception:
        # ignore drawing errors if window too small
        pass


def render(window, state):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)

    if not hasattr(state, "_fetch_stage"):
        state._fetch_stage = "fetching"
    if not hasattr(state, "_fetch_frame"):
        state._fetch_frame = 0

    h, w = window.getmaxyx()
    window.clear()
    window.box()

    title = f"Fetch: {state.branch}"
    tracking_name = getattr(state, "tracking_branch", None)
    if tracking_name:
        subtitle = f"Remote-tracking: {tracking_name}"
    else:
        subtitle = "No remote tracking branch"
    try:
        window.addstr(1, max(2, (w - len(title)) // 2), title,
                      curses.color_pair(cfg.STATUS_COLORS["magenta"]) | curses.A_BOLD)
        window.addstr(2, max(2, (w - len(subtitle)) // 2), subtitle,
                      curses.color_pair(cfg.STATUS_COLORS["magenta"]))
    except Exception:
        pass

    left_x = cfg.STATUS_X_POSITIONS.get("untracked", 5)
    right_x = cfg.STATUS_X_POSITIONS.get("committed", 65)
    line_y = cfg.ROW_Y + 2

    # Draw static parts
    LOCAL_NODES = 4
    _draw_commit_line(window, line_y + 1, left_x + 5, LOCAL_NODES, cfg.STATUS_COLORS["green"])
    try:
        window.addstr(line_y - 1, left_x,
                      f"[Local] ({state.branch}):",
                      curses.color_pair(cfg.STATUS_COLORS["green"]))
    except Exception:
        pass

    base_remote_nodes = 3
    _draw_commit_line(window, line_y + 1, right_x + 5, base_remote_nodes, cfg.STATUS_COLORS["cyan"])
    if tracking_name:
        remote_label = f"[Remote] {tracking_name}:"
    else:
        remote_label = "[Remote]:"
    try:
        window.addstr(line_y - 1, right_x, remote_label, curses.color_pair(cfg.STATUS_COLORS["cyan"]))
    except Exception:
        pass

    window.addstr(line_y + 5, left_x - 2, "Local Ref:", curses.color_pair(cfg.STATUS_COLORS["yellow"]))
    draw_box(window, line_y + 2, left_x + 8, 5, 9, cfg.STATUS_COLORS["yellow"], [(3, 4, "•")])

       # ===================== ANIMATION =====================
    if state._fetch_stage == "fetching":
        # Head of [Remote] line (source)
        remote_head_x = right_x + base_remote_nodes * 4
        remote_head_y = line_y + 2

        # Center of Local Ref box (destination)
        box_center_x = left_x + 8 + 4  # x of box + half width
        box_center_y = line_y + 2 + 4  # y of box + half height

        total_steps = 10
        step = state._fetch_frame % total_steps

        # Interpolate between source and destination
        fly_x = int(remote_head_x - (remote_head_x - box_center_x) * step / total_steps)
        fly_y = int(remote_head_y - (remote_head_y - box_center_y) * step / total_steps)

        try:
            window.addstr(fly_y, fly_x, FLYING_COMMIT_CHAR,
                          curses.color_pair(cfg.STATUS_COLORS["red"]) | curses.A_BOLD)
        except Exception:
            pass

        # Instruction note
        note = "Fetching commits... remote data moving to Local Ref"
        try:
            window.addstr(line_y + 7, max(4, (w - len(note)) // 2), note,
                          curses.color_pair(cfg.STATUS_COLORS["yellow"]))
        except Exception:
            pass

        state._fetch_frame += 1
        if step == total_steps - 1:
            # Once animation reaches end, switch stage to 'done'
            state._fetch_stage = "done"

    elif state._fetch_stage == "done":
        fetched = int(getattr(state, "behind", 0))
        total_remote_nodes = base_remote_nodes + max(0, fetched)
        # _draw_commit_line(window, line_y, right_x, total_remote_nodes, 2)

        # compute screen center
        h, w = window.getmaxyx()
        center_y = h // 2 + 2   # slight below vertical center
        center_x = w // 2

        try:
            if fetched > 0:

                msg1 = f"Fetched {fetched} new commit(s) for this branch."
            else:
                msg1 = "No new commits fetched for this branch."
            msg2 = "Commits fetched to remote-tracking refs, not merged into local branches ."

            # draw messages centered horizontally
            window.addstr(center_y, max(0, center_x - len(msg1)//2),
                          msg1, curses.color_pair(2 if fetched > 0 else 1))
            window.addstr(center_y + 1, max(0, center_x - len(msg2)//2),
                          msg2)
        except Exception:
            pass


    window.refresh()


def draw_box(win, y, x, height, width, color, symbols):
    """
    Draws an individual box with title and content.
    """
    win.attron(curses.color_pair(color))

    # Box outline
    win.addstr(y + 1, x, "┌" + "─" * (width - 2) + "┐")
    for i in range(2, height):
        win.addstr(y + i, x, "│" + " " * (width - 2) + "│")
    win.addstr(y + height, x, "└" + "─" * (width - 2) + "┘")

    # Symbols inside
    for sy, sx, sym in symbols:
        win.addstr(y + sy, x + sx, sym)

    win.attroff(curses.color_pair(color))


def start(window, git_state):
    """
    Start the fetch animation loop. It returns (stop_event, thread) as per animations.base.start_animation.
    """
    return start_animation(window, render, git_state)
