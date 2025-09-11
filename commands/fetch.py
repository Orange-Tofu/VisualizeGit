# commands/fetch.py
import time
from core import git_utils
from animations import fetch as fetch_anim

def run(top_window, runner):
    """
    Run git fetch animation + actual command execution.
    """
    git_state = git_utils.build_state()
    # For fetch, we need local + remote branch name
    git_state.remote_branch = git_utils.get_remote_branch_name(git_state.branch)
    git_state.tracking_branch = git_utils.get_tracking_branch()

    controller = fetch_anim.start(top_window, git_state)

    runner.run_and_stream()
    time.sleep(5)

    controller.stop()
    print("\n".join(runner.get_output()))
