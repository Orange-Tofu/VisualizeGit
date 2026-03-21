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
    commit_message = ""
    git_state = git_utils.build_state()
    git_state.speed = speed

    if "--amend" in user_cmd:
        if "--no-edit" in user_cmd:
            git_state.commit_type = "amend_no_edit"
        elif "-m" in user_cmd or "--message" in user_cmd:
            git_state.commit_type = "amend_with_m"
            for opt in ["-m", "--message"]:
                if opt in user_cmd:
                    idx = user_cmd.index(opt)
                    if idx + 1 < len(user_cmd):
                        commit_message = user_cmd[idx + 1]
        else:
            runner.layout_pane.update(Panel(Text("Interactive amend not supported"), title="Error", border_style="red"))
            return None
    elif "-m" in user_cmd or "--message" in user_cmd:
        git_state.commit_type = "commit_m"
        for opt in ["-m", "--message"]:
            if opt in user_cmd:
                idx = user_cmd.index(opt)
                if idx + 1 < len(user_cmd):
                    commit_message = user_cmd[idx + 1]
    else:
        runner.layout_pane.update(Panel(Text("Interactive commit not supported"), title="Error", border_style="red"))
        return None

    git_state.commit_message = commit_message or "New"

    def update_states():
        try:
            repo = Repo(".")
            last_commits = list(repo.iter_commits(git_state.branch, max_count=3))
            git_state.commit_hashes = [c.hexsha for c in reversed(last_commits)]
            git_state.commit_messages = [c.message.splitlines()[0] for c in reversed(last_commits)]
        except Exception as e:
            logger.debug(f"commit.run: could not pre-fetch commits: {e}")
            git_state.commit_hashes = []
            git_state.commit_messages = []

    update_states()

    controller = commit_anim.start(top_window, git_state)
    await runner.run_and_stream()

    # Refresh after command execution
    update_states()

    return controller
