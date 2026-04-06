# commands/checkout.py
import asyncio
from git import Repo, exc
from vgit.core import git_utils
from vgit.core.logger import logger
from vgit.animations import checkout as checkout_anim

async def run(top_window, runner, speed='normal'):
    """
    Handle git checkout animation & execution.
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
    
    # Default is a normal branch checkout
    git_state.checkout_type = "checkout"
    git_state.target_branch = "???"
    git_state.is_new_branch = False
    git_state.upstream_ref = None
    
    # Basic parsing for animation only
    # git checkout [-b|-B] <new_branch> [<start_point>]
    # git checkout <branch>
    # git checkout -- <file>
    
    if "-b" in git_args or "-B" in git_args:
        git_state.is_new_branch = True
        idx = git_args.index("-b") if "-b" in git_args else git_args.index("-B")
        if len(git_args) > idx + 1:
            git_state.target_branch = git_args[idx + 1]
        if len(git_args) > idx + 2:
            git_state.upstream_ref = git_args[idx + 2]
    elif "--" in git_args:
        # File checkout - move to unsupported/fallback
        # We handle this by letting the default animation take over if needed, 
        # or we can just run it. User said standard fallback.
        git_state.checkout_type = "unsupported"
        from vgit.animations import default
        controller = default.start(top_window, git_state)
        await runner.run_and_stream()
        return controller
    else:
        # Simple checkout <branch>
        # Positional arguments that aren't starts with -
        pos_args = [a for a in git_args if not a.startswith("-")]
        if pos_args:
            git_state.target_branch = pos_args[0]
            
    controller = checkout_anim.start(top_window, git_state)
    
    # Run the command
    exit_code, _lines = await runner.run_and_stream()
    
    if exit_code == 0:
        git_state.checkout_status = "success"
    else:
        git_state.checkout_status = "failed"
    
    return controller
