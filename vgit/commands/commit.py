import asyncio
from git import Repo, exc
from vgit.core import git_utils
from vgit.core.logger import logger
from vgit.animations import commit as commit_anim
from rich.panel import Panel
from rich.text import Text

async def run(top_window, runner, speed='normal'):
    """
    Handle git commit animation & execution.
    """
    user_cmd = runner.cmd
    repo = Repo(".")
    
    git_state = git_utils.build_state(repo=repo)
    git_state.speed = speed

    if "--amend" in user_cmd:
        if "--no-edit" in user_cmd:
            git_state.commit_type = "amend_no_edit"
        elif "-m" in user_cmd or "--message" in user_cmd:
            git_state.commit_type = "amend_with_m"
        else:
            runner.layout_pane.update(Panel(Text("Interactive amend not supported"), title="Error", border_style="red"))
            return None
    elif "-m" in user_cmd or "--message" in user_cmd:
        git_state.commit_type = "commit_m"
    else:
        runner.layout_pane.update(Panel(Text("Interactive commit not supported"), title="Error", border_style="red"))
        return None

    git_state.commit_message = git_utils.get_commit_message_from_args(user_cmd) or "New"

    def update_states(r):
        try:
            last_commits = list(r.iter_commits(git_state.branch, max_count=3))
            git_state.commit_hashes = [c.hexsha for c in reversed(last_commits)]
            git_state.commit_messages = [c.message.splitlines()[0] for c in reversed(last_commits)]
        except Exception as e:
            logger.debug(f"commit.run: could not fetch commits: {e}")
            git_state.commit_hashes = []
            git_state.commit_messages = []

    update_states(repo)
    # Record the base history for consistent animation even after refresh
    git_state.base_hashes = list(git_state.commit_hashes)
    git_state.base_messages = list(git_state.commit_messages)
    git_state.initial_commit_count = len(git_state.commit_hashes)

    controller = commit_anim.start(top_window, git_state)
    exit_code, _lines = await runner.run_and_stream()

    # Refresh after command execution
    update_states(repo)
    
    # If it failed, let animation know or stop it
    if exit_code != 0:
        # We can change the commit type to something that render() handles specially
        git_state.commit_type = 'failed'

    return controller
