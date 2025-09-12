# core/git_utils.py
from git import Repo
from core.git_model import GitState

def build_state(path="."):
    repo = Repo(path)

    staged = sum(1 for _ in repo.index.diff("HEAD"))
    changed = sum(1 for _ in repo.index.diff(None))
    untracked = len(repo.untracked_files)
    branch = repo.active_branch.name

    return GitState(staged, changed, untracked, branch)


def get_ahead_behind(path="."):
    """
    Returns (ahead, behind) commit counts relative to remote.
    If no remote or detached HEAD, returns (-1, -1).
    """
    repo = Repo(path)
    ahead = behind = -1

    try:
        tracking_branch = repo.active_branch.tracking_branch()
        if tracking_branch:
            commits_behind = repo.iter_commits(f"{repo.active_branch.name}..{tracking_branch}")
            commits_ahead = repo.iter_commits(f"{tracking_branch}..{repo.active_branch.name}")
            ahead = sum(1 for _ in commits_ahead)
            behind = sum(1 for _ in commits_behind)
    except Exception:
        # If detached HEAD, no upstream, etc.
        ahead, behind = -1, -1

    return ahead, behind


def get_remote_branch_name(branch):
    """
    Get the remote tracking branch name for the given local branch.
    Returns e.g. 'origin/main' if tracking exists, else '<no remote>'.
    """
    repo = Repo(".")
    try:
        tracking_branch = repo.active_branch.tracking_branch()
        return tracking_branch.name if tracking_branch else "<no remote>"
    except Exception:
        return "<no remote>"
      

def get_tracking_branch():
    repo = Repo(".")
    branch = repo.active_branch
    tracking = branch.tracking_branch()
    if tracking:
        return tracking.name  # e.g. 'origin/main'
    return None