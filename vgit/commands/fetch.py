# commands/fetch.py
import asyncio
from vgit.core import git_utils
from vgit.animations import fetch as fetch_anim

async def run(top_window, runner, speed='normal'):
    """
    Run git fetch animation + actual command execution.
    """
    git_state = git_utils.build_state()
    # For fetch, we need local + remote branch name
    git_state.remote_branch = git_utils.get_remote_branch_name(git_state.branch)
    git_state.tracking_branch = git_utils.get_tracking_branch()
    git_state.speed = speed

    controller = fetch_anim.start(top_window, git_state)
    await runner.run_and_stream()
    
    return controller