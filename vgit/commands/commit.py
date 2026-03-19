import asyncio
from git import Repo
from vgit.core import git_utils
from vgit.animations import commit as commit_anim
from rich.panel import Panel
from rich.text import Text

async def run(top_window, runner, speed='normal'):
    """
    Handle git commit animation & execution.
    """
    user_cmd = runner.cmd  # full command list, e.g. ['git','commit','-m','msg']
    commit_message = ""
    git_state = git_utils.build_state()
    git_state.speed = speed

    if "--amend" in user_cmd:
        if "--no-edit" in user_cmd:
            git_state.commit_type = "amend_no_edit"
        elif "-m" in user_cmd or "--message" in user_cmd:
            git_state.commit_type = "amend_with_m"
            if "-m" in user_cmd:
                m_index = user_cmd.index("-m")
                if m_index + 1 < len(user_cmd):
                    commit_message = user_cmd[m_index + 1]
            elif "--message" in user_cmd:
                m_index = user_cmd.index("--message")
                if m_index + 1 < len(user_cmd):
                    commit_message = user_cmd[m_index + 1]
        else:
            runner.layout_pane.update(Panel(Text("Interactive amend not supported"), title="Error", border_style="red"))
            return
    elif "-m" in user_cmd or "--message" in user_cmd:
            git_state.commit_type = "commit_m"
            if "-m" in user_cmd:
                m_index = user_cmd.index("-m")
                if m_index + 1 < len(user_cmd):
                    commit_message = user_cmd[m_index + 1]
            elif "--message" in user_cmd:
                m_index = user_cmd.index("--message")
                if m_index + 1 < len(user_cmd):
                    commit_message = user_cmd[m_index + 1]
    else:
        runner.layout_pane.update(Panel(Text("Interactive commit not supported"), title="Error", border_style="red"))
        return

    git_state.commit_message = commit_message or "New"

    # Preload last commits
    repo = Repo(".")
    last_commits = list(repo.iter_commits(git_state.branch, max_count=3))
    git_state.commit_hashes = [c.hexsha for c in reversed(last_commits)]
    git_state.commit_messages = [c.message.splitlines()[0] for c in reversed(last_commits)]

    controller = commit_anim.start(top_window, git_state)
    await runner.run_and_stream()

    # After commit, reload commits (so HEAD moves)
    repo = Repo(".")
    last_commits = list(repo.iter_commits(git_state.branch, max_count=3))
    git_state.commit_hashes = [c.hexsha for c in reversed(last_commits)]
    git_state.commit_messages = [c.message.splitlines()[0] for c in reversed(last_commits)]

    pause = 4.0 if speed == 'normal' else (2.0 if speed == 'fast' else 8.0)
    await asyncio.sleep(pause)
    await controller.stop()
