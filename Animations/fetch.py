# animations/fetch.py
import curses
from animations.base import start_animation
from core import ui_config as cfg

COMMIT_CHAR = "●"
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
    """
    Frame-by-frame renderer called repeatedly by animations.base.start_animation.
    We rely on state._fetch_stage and state._fetch_frame to drive the animation.
      - _fetch_stage: 'fetching' | 'done'
      - _fetch_frame: integer frame counter
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # local branch
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)    # remote-tracking
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # flying commits / highlight
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # labels / notes

    # Initialize animation state on the git_state object if missing
    if not hasattr(state, "_fetch_stage"):
        state._fetch_stage = "fetching"
    if not hasattr(state, "_fetch_frame"):
        state._fetch_frame = 0

    h, w = window.getmaxyx()
    window.clear()
    window.box()

    # HEADLINE
    title = f"Fetch: {state.branch}"
    subtitle = f"Remote-tracking: origin/{state.branch}"
    try:
        window.addstr(1, max(2, (w - len(title)) // 2), title, curses.color_pair(4) | curses.A_BOLD)
        window.addstr(2, max(2, (w - len(subtitle)) // 2), subtitle, curses.color_pair(4))
    except Exception:
        pass

    # Determine positions (use centralized config X positions when it makes sense)
    left_x = cfg.STATUS_X_POSITIONS.get("untracked", 5)      # local branch area
    right_x = cfg.STATUS_X_POSITIONS.get("committed", 65)    # remote-tracking area
    line_y = cfg.ROW_Y + 2

    # Draw Local branch (fixed small number of nodes, visually representing history)
    LOCAL_NODES = 4
    _draw_commit_line(window, line_y + 1, left_x + 5, LOCAL_NODES, 1)
    try:
        window.addstr(line_y - 1, left_x, f"[Local] ({state.branch}):", curses.color_pair(1))
    except Exception:
        pass

    # Draw Remote-tracking (base nodes)
    base_remote_nodes = 3
    _draw_commit_line(window, line_y + 1, right_x + 5, base_remote_nodes, 2)
    try:
        window.addstr(line_y - 1, right_x, f"[Remote] origin/({state.branch}):", curses.color_pair(2))
    except Exception:
        pass

    # Animation behavior:
    # - while fetching (state._fetch_stage == 'fetching') => show a looping "flying commit" moving from remote cloud to remote-tracking
    # - when done (state._fetch_stage == 'done') => show final remote-tracking line augmented with state.behind commits,
    #   and show explanatory note that local is unchanged.

    if state._fetch_stage == "fetching":
        # continuously animate a flying commit from a 'remote cloud' toward the remote-tracking line.
        # We compute a cycling position using _fetch_frame.
        cycle = state._fetch_frame % 8  # 0..7
        start_x = right_x + 14  # remote cloud source
        target_base = right_x + base_remote_nodes * 4  # where new commits will appear
        # computed flying x: move leftwards toward target_base
        # interpolate between start_x and target_base
        t = cycle / 8.0
        fly_x = int(start_x - (start_x - target_base) * t)

        # draw a small "remote cloud" icon
        cloud_x = start_x - 6
        try:
            window.addstr(line_y - 2, cloud_x, "[REMOTE]", curses.color_pair(2))
        except Exception:
            pass

        # draw the flying commit
        try:
            window.addstr(line_y - 1, fly_x, COMMIT_CHAR, curses.color_pair(3) | curses.A_BOLD)
        except Exception:
            pass

        # small instruction text
        note = "Fetching commits... remote-tracking refs updating (local branch unchanged)"
        try:
            window.addstr(line_y + 3, max(4, (w - len(note)) // 2), note, curses.color_pair(4))
        except Exception:
            pass

        # advance frame counter for next render call
        state._fetch_frame += 1

    elif state._fetch_stage == "done":
        # show final remote-tracking commits based on state.behind
        fetched = int(getattr(state, "behind", 0))
        # draw base + fetched commits
        total_remote_nodes = base_remote_nodes + max(0, fetched)
        _draw_commit_line(window, line_y, right_x, total_remote_nodes, 2)

        # explanatory text
        try:
            if fetched > 0:
                window.addstr(line_y + 2, left_x, f"Fetched {fetched} new commit(s).", curses.color_pair(2))
            else:
                window.addstr(line_y + 2, left_x, "No new commits fetched.", curses.color_pair(1))
            window.addstr(line_y + 4, left_x, "Local branch unchanged.", curses.color_pair(1))
        except Exception:
            pass

    window.refresh()

def start(window, git_state):
    """
    Start the fetch animation loop. It returns (stop_event, thread) as per animations.base.start_animation.
    """
    return start_animation(window, render, git_state)
