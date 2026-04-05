# commands/push.py
import asyncio
from git import Repo, exc
from vgit.core import git_utils
from vgit.core.logger import logger
from vgit.animations import push as push_anim

async def run(top_window, runner, speed='normal'):
    """
    Handle git push animation & execution.
    """
    repo = Repo(".")
    git_state = git_utils.build_state(repo=repo)
    ahead, behind = git_utils.get_ahead_behind(repo=repo)
    git_state.ahead = ahead
    git_state.behind = behind
    git_state.tracking_branch = git_utils.get_tracking_branch(repo=repo)
    git_state.speed = speed
    
    user_cmd = runner.cmd
    
    # Analyze the command to determine push_type for animation
    if "--set-upstream" in user_cmd or "-u" in user_cmd:
        git_state.push_type = "upstream"
    elif ahead == 0:
        git_state.push_type = "up_to_date"
    elif "--force" in user_cmd or "-f" in user_cmd:
        git_state.push_type = "force"
    elif behind > 0:
        # Pushing when behind might lead to rejection
        git_state.push_type = "rejected"
    else:
        git_state.push_type = "normal"
        
    controller = push_anim.start(top_window, git_state)
    exit_code, _lines = await runner.run_and_stream()
    
    # Update logic post-push
    if exit_code != 0:
        git_state.push_type = "rejected"
    elif git_state.push_type != "force" and git_state.push_type != "upstream":
        # Only overwrite status if it wasn't a special type (force/upstream)
        git_state.push_type = "done"

    return controller
