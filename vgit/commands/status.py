
from vgit.core import git_utils
from vgit.animations import status as status_anim
from vgit.core.ui_utils import wait_for_button_press

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
    controller.stop()
    wait_for_button_press(top_window)
    print("\n".join(runner.get_output()))