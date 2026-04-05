# commands/add.py
import asyncio
from git import Repo, exc
from vgit.core import git_utils
from vgit.core.logger import logger
from vgit.animations import add as add_anim

async def run(top_window, runner, speed='normal'):
    """
    Handle git add animation & execution.
    """
    repo = Repo(".")
    # Initial state
    git_state = git_utils.build_state(repo=repo)
    git_state.speed = speed
    git_state.initial_staged = git_state.staged
    git_state.initial_unstaged = git_state.changed + git_state.untracked
    
    # Determine what is being added
    # We can peek at the runner.cmd (e.g. ['git', 'add', '.'])
    user_cmd = runner.cmd
    
    # Estimate how many files will be added
    # This is a bit tricky without running dry-run, but we can guess.
    if "." in user_cmd or "-A" in user_cmd or "--all" in user_cmd:
        git_state.to_add_count = git_state.changed + git_state.untracked
    else:
        # Specific files - count non-flag arguments after 'add'
        git_state.to_add_count = sum(1 for arg in user_cmd[2:] if not arg.startswith("-"))
    
    controller = add_anim.start(top_window, git_state)
    
    # Run the command
    exit_code, _lines = await runner.run_and_stream()
    
    # Final state update
    final_state = git_utils.build_state(repo=repo)
    git_state.staged = final_state.staged
    git_state.changed = final_state.changed
    git_state.untracked = final_state.untracked
    
    if exit_code == 0:
        git_state.add_status = "success"
    else:
        git_state.add_status = "failed"

    return controller
