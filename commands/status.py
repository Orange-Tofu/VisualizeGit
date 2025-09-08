# commands/status.py
import time
from core import git_utils
from animations import status as status_anim

def run(top_window, runner):
    """
    Run the git status animation (top) while streaming the real command (bottom).
    """
    git_state = git_utils.build_state()
    ahead, behind = git_utils.get_ahead_behind()
    git_state.ahead = ahead
    git_state.behind = behind

    stop_event, anim_thread = status_anim.start(top_window, git_state)
    runner.run_and_stream()
    time.sleep(5)

    stop_event.set()
    anim_thread.join()

    print("\n".join(runner.get_output()))
