import curses
from animations.base import start_animation
from core import ui_config as cfg

COMMIT_CHAR = "◉"
LINK = "    ──▶──▶"  # double arrow for spacing


def render(window, state):
    """
    Animation for git commit -m.
    We assume state contains:
      - branch
      - commit_message
      - commit_hashes (list of latest commit hashes, newest last)
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # HEAD
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)    # old commits
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # text
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)     # new commit

    if not hasattr(state, "_frame"):
        state._frame = 0

    window.clear()
    window.box()

    # compute commits and spacing
    h, w = window.getmaxyx()
    start_x = 10
    y = cfg.ROW_Y + 5
    frame = state._frame

    # get up to last 3 commits (oldest first)
    commits = state.commit_hashes[-3:] if hasattr(state, "commit_hashes") else []
    commits_display = [""] * (3 - len(commits)) + commits  # right-align if fewer than 3

    commits_x = []
    for i, chash in enumerate(commits_display):
        x = start_x + i * 18  # more spacing for double arrow
        commits_x.append(x)

        # draw commit circle
        try:
            window.addstr(y, x, COMMIT_CHAR, curses.color_pair(2))
        except Exception:
            pass

        hash_txt = "#→ " + chash[:4] if chash else "----"
        try:
            window.addstr(y - 2, x - 2, hash_txt, curses.color_pair(3))
        except Exception:
            pass

        # draw message below
        if hasattr(state, "commit_messages") and len(state.commit_messages) > i:
            msg_txt = f"\"{state.commit_messages[i][:8]}\""
        else:
            msg_txt = f"Commit{i+1}"
        try:
            window.addstr(y + 2, x - len(msg_txt)//2, msg_txt, curses.color_pair(3))
        except Exception:
            pass

        # draw link to next
        if i < 2:
            try:
                window.addstr(y, x + 2, LINK, curses.color_pair(2))
            except Exception:
                pass

    # HEAD pointer starts at last commit initially
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
        # draw arrow to new commit
        try:
            window.addstr(y, head_x + 2, LINK, curses.color_pair(4))
        except Exception:
            pass
        # draw new commit circle
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

    try:
        window.addstr(y - 4, head_label_x, "HEAD", curses.color_pair(1))
        window.addstr(y - 3, head_arrow_x, "↓", curses.color_pair(1))
    except Exception:
        pass

    note = f"Branch: {state.branch} – Adding new commit..."
    try:
        window.addstr(y + 6, max(4, (w - len(note)) // 2),
                      note, curses.color_pair(3))
    except Exception:
        pass

    state._frame += 1
    window.refresh()


def start(window, git_state):
    """
    Start the commit animation loop. It returns (stop_event, thread).
    """
    return start_animation(window, render, git_state)
