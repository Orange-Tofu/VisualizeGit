import curses
from vgit.animations.base import start_animation
from vgit.core import ui_config as cfg


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


def _draw_staging_box(win, y, x, color):
    """Draw the staging area box to the right of commits."""
    try:
        win.attron(curses.color_pair(color))
        win.addstr(y, x, "┌──────── STAGING AREA ──────┐")
        win.addstr(y + 1, x, "│                            │")
        win.addstr(y + 2, x, "│    • Existing changes      │")
        win.addstr(y + 3, x, "│                            │")
        win.addstr(y + 4, x, "└────────────────────────────┘")
        win.attroff(curses.color_pair(color))
    except Exception:
        pass



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

def render_commit_amend(window, state):
    """
    Animation for git commit --amend (non-interactive).
    Shows taking files from last commit into staging area,
    then creating a replacement commit.
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # HEAD
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)    # old commits
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # text
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)     # new/replaced commit
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)      # staging box
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK) 

    if not hasattr(state, "_frame"):
        state._frame = 0

    window.clear()
    window.box()

    # basic layout
    h, w = window.getmaxyx()
    start_x = 10
    y = cfg.ROW_Y + 5
    frame = state._frame

    # draw existing commits (green) and links
    commits_x = _render_existing_commits(window, state, y, start_x)

    # HEAD pointer at last commit
    head_x = commits_x[-1]

    note_top = f"Branch: {state.branch} – Amending commit..."
    try:
        window.addstr(1, max(4, (w - len(note_top)) // 2),
                      note_top, curses.color_pair(3))
    except Exception:
        pass

    # staging area box to the right of branch
    staging_x = head_x + 22
    staging_y = y - 3
    

    # stage messages
    if frame <= 4:
        note = "Files moved to staging area..."
    elif frame < 9:
        note = "Creating replacement commit..."
    else:
        note = "Replaced old commit with amended commit."
    try:
        window.addstr(y + 8, max(4, (w - len(note)) // 2), note,
                      curses.color_pair(3))
    except Exception:
        pass

    # first half: files flying into staging
    if frame <= 2:
        fly_x = head_x + int((staging_x - head_x) * (frame / 4))
        try:
            window.addstr(y, fly_x, "🡲", curses.color_pair(3))
        except Exception:
            pass
        txt = "Changes from last commit moved to staging..."
        try:
            window.addstr(y - 6, max(4, (w - len(txt)) // 2),
                          txt, curses.color_pair(3))
        except Exception:
            pass
        _draw_staging_box(window, staging_y, staging_x, color=4)

    
    elif 3 <= frame <= 6:
        # Files flying back from staging to commit
        fly_x = staging_x - int(((frame-4) * (staging_x - head_x)) / 4)
        try:
            window.addstr(y, fly_x, "🡰", curses.color_pair(5))
        except Exception:
            pass
        txt = "Staging changes merged into amended commit..."
        try:
            window.addstr(y - 6, max(4, (w - len(txt)) // 2),
                          txt, curses.color_pair(3))
        except Exception:
            pass

        _draw_staging_box(window, staging_y, staging_x, color=6)


    # second half: replaced commit appears at old commit location
    elif frame >= 7:
        # Clear old hash/message area first to avoid overlap
        try:
            window.addstr(y - 2, head_x - 4, " " * 10)
            window.addstr(y + 2, head_x - 6, " " * 14)
        except Exception:
            pass

        msg_txt = f"\"{state.commit_message[:8]}\""
        _draw_commit(window, head_x, y, state.commit_hashes[-1],
                     msg_txt, curses.color_pair(4), curses.color_pair(3))

        _draw_staging_box(window, staging_y, staging_x, color=6)

    # HEAD pointer moves to replaced commit after frame 9
    head_label_x = head_x - 2
    head_arrow_x = head_x
    try:
        window.addstr(y - 4, head_label_x, "HEAD", curses.color_pair(1))
        window.addstr(y - 3, head_arrow_x, "↓", curses.color_pair(1))
    except Exception:
        pass

    # branch label
    branch_note = f"Branch: {state.branch} – Amending last commit..."
    try:
        window.addstr(y + 10, max(4, (w - len(branch_note)) // 2),
                      branch_note, curses.color_pair(3))
    except Exception:
        pass

    state._frame += 1
    window.refresh()


def render(window, state):
    """
    Orchestrator for git commit -m animation.
    """
    ctype = getattr(state, "commit_type", "commit_m")
    if ctype == "commit_m":
        render_commit_m(window, state)
    elif ctype in ("amend_no_edit", "amend_with_m"):
        render_commit_amend(window, state)
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
