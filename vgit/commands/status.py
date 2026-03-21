# commands/status.py
import asyncio
from vgit.core import git_utils
from vgit.animations import status as status_anim

async def run(top_window, runner, speed='normal'):
    """
    Run the git status animation (top) while streaming the real command (bottom).
    """
    git_state = git_utils.build_state()
    ahead, behind = git_utils.get_ahead_behind()
    git_state.ahead = ahead
    git_state.behind = behind
    git_state.speed = speed

    controller = status_anim.start(top_window, git_state)
    await runner.run_and_stream()
    
    return controller
