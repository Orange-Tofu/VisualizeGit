# commands/status.py
import time
from core import git_utils
from animations import status as status_anim

def run(top_window, runner):
    """
    Run the git status animation (top) while streaming the real command (bottom).
    """
    # Build current repo state
    git_state = git_utils.build_state()
    ahead, behind = git_utils.get_ahead_behind()
    git_state.ahead = ahead
    git_state.behind = behind

    # Start the animation in a thread
    stop_event, anim_thread = status_anim.start(top_window, git_state)

    # Stream the real command output
    runner.run_and_stream()

    # Wait 5 seconds before closing
    time.sleep(5)

    # Stop animation thread cleanly
    stop_event.set()
    anim_thread.join()

    # After curses exits, print output back to terminal
    print("\n".join(runner.get_output()))
