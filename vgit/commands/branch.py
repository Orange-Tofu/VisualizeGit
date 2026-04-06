# commands/branch.py
import asyncio
from git import Repo, exc
from vgit.core import git_utils
from vgit.core.logger import logger
from vgit.animations import checkout as checkout_anim

async def run(top_window, runner, speed='normal'):
    """
    Handle git branch operations (deletion, creation, etc.)
    Currently focus on deletion animation.
    """
    repo = Repo(".")
    git_state = git_utils.build_state(repo=repo)
    git_state.speed = speed
    
    def update_commits(r):
        try:
             commits = list(r.iter_commits(git_state.branch, max_count=3))
             git_state.base_hashes = [c.hexsha for c in reversed(commits)]
             git_state.base_messages = [c.message.splitlines()[0] for c in reversed(commits)]
        except:
             pass
    
    update_commits(repo)
    
    # Analyze arguments
    user_cmd = runner.cmd
    git_args = user_cmd[2:]
    
    # Check for deletion
    if "-d" in git_args or "-D" in git_args or "--delete" in git_args:
        git_state.checkout_type = "delete_branch"
        
        # Determine branch to delete
        # For simplicity, find first non-flag
        pos_args = [a for a in git_args if not a.startswith("-")]
        if pos_args:
            git_state.delete_branch_name = pos_args[0]
        
        controller = checkout_anim.start(top_window, git_state)
    else:
        # Other branch operations might not be animated specifically yet
        # Fall back to default/unsupported display
        from vgit.animations import default
        controller = default.start(top_window, git_state)
    
    # Run the command
    exit_code, _lines = await runner.run_and_stream()
    
    if exit_code == 0:
        git_state.checkout_status = "success"
    else:
        git_state.checkout_status = "failed"
    
    return controller
