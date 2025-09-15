# vgit/commands/clone.py
from git import Repo
from vgit.core import git_utils
from vgit.animations import clone as clone_anim
from vgit.animations import commit as commit_anim

import os
import time

def run(top_window, runner):
    """
    Handle git clone animation & execution.
    """
    user_cmd = runner.cmd  # e.g. ['git', 'clone', 'https://...', 'mydir']
    git_state = git_utils.build_state()

    if len(user_cmd) < 3:
        runner.window.addstr(1, 2, "Usage: git clone <repo-url> [directory]")
        runner.window.refresh()
        return

    repo_url = user_cmd[2]
    target_dir = None
    if len(user_cmd) >= 4:
        target_dir = user_cmd[3]

    # Fill state for animation
    git_state.remote_url = repo_url
    git_state.repo_name = os.path.basename(repo_url).replace(".git", "")
    git_state.total_files = 20  # rough guess; animation fakes progress if unknown

    # Start animation controller
    controller = clone_anim.start(top_window, git_state)

    # Run the actual git clone command
    runner.run_and_stream()

    # After clone, if target dir exists, inspect repo to get real stats
    repo_path = target_dir or git_state.repo_name
    if os.path.isdir(repo_path):
        try:
            repo = Repo(repo_path)
            # Just count tracked files in HEAD
            files = [f for f in repo.git.ls_files().splitlines()]
            git_state.files = files
            git_state.total_files = len(files)
            # Update state to force "done"
            git_state._clone_stage = "done"
        except Exception:
            pass

    # let animation play out a bit before stopping
    time.sleep(5)
    controller.stop()
