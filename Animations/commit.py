import curses
from animations.base import start_animation
from core import ui_config as cfg


COMMIT_CHAR = "◉"
LINK = "    ──▶──▶"  # double arrow for spacing


def _draw_commit(window, x, y, chash, msg_txt, color_commit, color_text):
    """Draw one commit with its hash and message."""
    try:
        window.addstr(y, x, COMMIT_CHAR, color_commit)
    except Exception:
        pass
    hash_txt = "#→ " + chash[:4] if chash else "----"
    try:
        window.addstr(y - 2, x - 2, hash_txt, color_text)
    except Exception:
        pass
    try:
        window.addstr(y + 2, x - len(msg_txt)//2, msg_txt, color_text)
    except Exception:
        pass


def _draw_link(window, x, y, color):
    """Draw arrow link between commits."""
    try:
        window.addstr(y, x, LINK, color)
    except Exception:
        pass


def _draw_head(window, head_label_x, head_arrow_x, y, color):
    """Draw HEAD label and arrow above a commit."""
    try:
        window.addstr(y - 4, head_label_x, "HEAD", color)
        window.addstr(y - 3, head_arrow_x, "↓", color)
    except Exception:
        pass


def _render_existing_commits(window, state, y, start_x):
    """Draw up to last 3 commits and return their X coordinates."""
    commits = state.commit_hashes[-3:] if hasattr(state, "commit_hashes") else []
    commits_display = [""] * (3 - len(commits)) + commits  # right-align

    commits_x = []
    for i, chash in enumerate(commits_display):
        x = start_x + i * 18
        commits_x.append(x)

        # message below each commit
        if hasattr(state, "commit_messages") and len(state.commit_messages) > i:
            msg_txt = f"\"{state.commit_messages[i][:8]}\""
        else:
            msg_txt = f"Commit{i+1}"

        _draw_commit(window, x, y, chash, msg_txt,
                     curses.color_pair(2), curses.color_pair(3))

        if i < 2:  # link to next commit
            _draw_link(window, x + 2, y, curses.color_pair(2))

    return commits_x


def _render_base(window, state):
    """Draw the base commits (last 3) with arrows."""
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # HEAD
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)    # old commits
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # text
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)     # new commit

    h, w = window.getmaxyx()
    start_x = 10
    y = 10

    commits = state.commit_hashes[-3:] if hasattr(state, "commit_hashes") else []
    commits_display = [""] * (3 - len(commits)) + commits  # right-align

    commits_x = []
    for i, chash in enumerate(commits_display):
        x = start_x + i * 18
        commits_x.append(x)

        msg_txt = (state.commit_messages[i] if hasattr(state, "commit_messages") and len(state.commit_messages) > i else "")
        _draw_commit_node(window, x, y, chash, msg_txt, curses.color_pair(2), curses.color_pair(3))

        # draw link to next commit
        if i < 2:
            _draw_link(window, x + 2, y, curses.color_pair(2))

    return commits_x, y  # return coordinates so main renderers can extend

def render_commit_m(window, state):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # HEAD
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)    # old commits
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # text
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)     # new commit

    if not hasattr(state, "_frame"):
        state._frame = 0

    window.clear()
    window.box()

    h, w = window.getmaxyx()
    start_x = 10
    y = cfg.ROW_Y + 5
    frame = state._frame

    # draw the three (old) commits exactly as before
    commits_x = _render_existing_commits(window, state, y, start_x)

    head_x = commits_x[-1]
    new_commit_x = head_x + 18

    # animate new commit flying in
    if frame < 6:
        fly_x = head_x + int((18 * frame) / 6)
        try:
            window.addstr(y, fly_x, COMMIT_CHAR, curses.color_pair(4))
        except Exception:
            pass
    else:
        _draw_link(window, head_x + 2, y, curses.color_pair(4))
        try:
            window.addstr(y, new_commit_x, COMMIT_CHAR, curses.color_pair(4))
            window.addstr(y + 2, new_commit_x - 4,
                          f"\"{state.commit_message[:8]}\"", curses.color_pair(3))
        except Exception:
            pass

    # HEAD pointer moves to new commit
    if frame < 6:
        head_label_x = head_x - 2
        head_arrow_x = head_x
    else:
        head_label_x = new_commit_x - 2
        head_arrow_x = new_commit_x

    _draw_head(window, head_label_x, head_arrow_x, y, curses.color_pair(1))

    note = f"Branch: {state.branch} – Adding new commit..."
    try:
        window.addstr(y + 6, max(4, (w - len(note)) // 2),
                      note, curses.color_pair(3))
    except Exception:
        pass

    state._frame += 1
    window.refresh()


def render_amend(window, state):
    """Placeholder for amend animation, reuse base for now."""
    window.clear()
    window.box()
    commits_x, y = _render_base(window, state)
    _draw_head_pointer(window, commits_x[-1], y, curses.color_pair(1))
    window.addstr(y + 6, 5, f"Amend commit placeholder...", curses.color_pair(3))
    window.refresh()


def render(window, state):
    """
    Orchestrator for git commit -m animation.
    """
    ctype = getattr(state, "commit_type", "commit_m")
    if ctype == "commit_m":
        render_commit_m(window, state)
    elif ctype in ("amend_no_edit", "amend_with_m"):
        render_amend(window, state)
    else:
        window.clear()
        window.box()
        window.addstr(2, 2, "Unsupported commit animation")
        window.refresh()




def start(window, git_state):
    """
    Start the commit animation loop. It returns (stop_event, thread).
    """
    return start_animation(window, render, git_state)
