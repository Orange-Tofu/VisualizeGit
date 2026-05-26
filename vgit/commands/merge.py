# commands/merge.py
import asyncio
from vgit.core import git_utils
from vgit.animations import merge as merge_anim
from git import Repo, exc
from vgit.core.logger import logger

async def run(top_window, runner, speed='normal'):
    """
    Run git merge animation + actual command execution.
    """
    repo = Repo(".")
    git_state = git_utils.build_state(repo=repo)
    git_state.speed = speed
    git_state.runner = runner  # Allow animation to monitor output
    
    # Parse arguments
    git_args = runner.cmd[2:] if len(runner.cmd) > 2 else []
    
    # Extract target branch/commit from arguments (first non-option argument)
    target_branch = None
    for arg in git_args:
        if not arg.startswith("-"):
            target_branch = arg
            break
            
    # Default state properties
    git_state.target_branch = target_branch or "<none>"
    git_state.is_no_ff = "--no-ff" in git_args
    git_state.ahead = 0
    git_state.behind = 0
    git_state.merge_type = "merge"
    
    if not target_branch:
        git_state.merge_type = "error"
    else:
        try:
            active_commit = repo.head.commit
            target_commit = repo.commit(target_branch)

            # Populate base commits (Active branch)
            try:
                active_commits = list(repo.iter_commits(active_commit, max_count=3))
                git_state.base_hashes = [c.hexsha for c in reversed(active_commits)]
                git_state.base_messages = [c.message.splitlines()[0] for c in reversed(active_commits)]
            except Exception as e:
                logger.debug(f"Error resolving active commits: {e}")

            # Populate target commits
            try:
                target_commits = list(repo.iter_commits(target_commit, max_count=3))
                git_state.target_hashes = [c.hexsha for c in reversed(target_commits)]
                git_state.target_messages = [c.message.splitlines()[0] for c in reversed(target_commits)]
            except Exception as e:
                logger.debug(f"Error resolving target commits: {e}")
            
            # Find merge base
            merge_bases = repo.merge_base(active_commit, target_commit)
            merge_base = merge_bases[0] if merge_bases else None
            
            if target_commit == active_commit or repo.is_ancestor(target_commit, active_commit):
                git_state.merge_type = "up_to_date"
            elif repo.is_ancestor(active_commit, target_commit):
                if git_state.is_no_ff:
                    git_state.merge_type = "merge"
                else:
                    git_state.merge_type = "ff"
            else:
                git_state.merge_type = "merge"
                
            if merge_base:
                git_state.behind = sum(1 for _ in repo.iter_commits(f"{merge_base.hexsha}..{target_commit.hexsha}"))
                git_state.ahead = sum(1 for _ in repo.iter_commits(f"{merge_base.hexsha}..{active_commit.hexsha}"))
        except Exception as e:
            logger.debug(f"Error determining merge type: {e}")
            git_state.merge_type = "error"
            
    controller = merge_anim.start(top_window, git_state)
    await runner.run_and_stream()
    return controller
