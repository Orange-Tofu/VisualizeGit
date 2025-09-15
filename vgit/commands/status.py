# commands/status.py
import time
from vgit.core import git_utils
from vgit.animations import status as status_anim

def run(top_window, runner):
    """
    Run the git status animation (top) while streaming the real command (bottom).
    """
    git_state = git_utils.build_state()
    ahead, behind = git_utils.get_ahead_behind()
    git_state.ahead = ahead
    git_state.behind = behind

    controller = status_anim.start(top_window, git_state)
    runner.run_and_stream()
    # Wait until user presses SPACE/'q' to stop animation
    try:
        top_window.nodelay(True)
        top_window.keypad(True)
    except Exception:
        pass
    while True:
        if controller.is_stopped():
            break
        try:
            ch = top_window.getch()
            if ch in (32, ord('q')):
                controller.stop()
                break
        except Exception:
            pass
        time.sleep(0.05)

    print("\n".join(runner.get_output()))
