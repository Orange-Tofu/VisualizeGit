# commands/pull.py
import asyncio
import subprocess
from vgit.core import git_utils
from vgit.animations import pull as pull_anim
from git import Repo, exc

async def run(top_window, runner, speed='normal'):
    """
    Run git pull animation + actual command execution.
    """
    repo = Repo(".")
    git_state = git_utils.build_state(repo=repo)
    
    # Pre-checks for pull
    git_state.remote_branch = git_utils.get_remote_branch_name(git_state.branch, repo=repo)
    git_state.tracking_branch = git_utils.get_tracking_branch(repo=repo)
    git_state.speed = speed
    
    git_args = runner.cmd[2:] if len(runner.cmd) > 2 else []
    git_state.is_rebase = "--rebase" in git_args
    git_state.runner = runner # Allow animation to monitor output
    
    # Determine ahead/behind
    # For a smoother animation, we'll fetch explicitly first to get the behind count.
    try:
        repo.remotes.origin.fetch()
    except:
        pass
        
    ahead, behind = git_utils.get_ahead_behind(repo=repo)
    git_state.ahead = ahead
    git_state.behind = behind
    
    if not git_state.tracking_branch:
         git_state.pull_type = 'error'
    elif behind == 0:
         git_state.pull_type = 'up_to_date'
    else:
         if git_state.is_rebase:
              git_state.pull_type = 'rebase'
         elif ahead == 0:
              git_state.pull_type = 'ff'
         else:
              git_state.pull_type = 'merge'
    
    controller = pull_anim.start(top_window, git_state)
    await runner.run_and_stream()
    return controller
