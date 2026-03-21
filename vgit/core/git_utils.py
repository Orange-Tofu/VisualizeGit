from git import Repo, exc
from vgit.core.git_model import GitState
from vgit.core.logger import logger

def build_state(path="."):
    """Safely construct the GitState. Returns a zeroed state if not a git repo."""
    try:
        repo = Repo(path)
        staged = sum(1 for _ in repo.index.diff("HEAD"))
        changed = sum(1 for _ in repo.index.diff(None))
        untracked = len(repo.untracked_files)
        branch = repo.active_branch.name
        return GitState(staged, changed, untracked, branch)
    except (exc.InvalidGitRepositoryError, exc.NoSuchPathError, NameError, AttributeError) as e:
        logger.debug(f"build_state: not a git repository or no branch: {e}")
        return GitState(0, 0, 0, "<no branch>")
    except Exception as e:
        logger.error(f"Unexpected error in build_state: {e}", exc_info=True)
        return GitState(0, 0, 0, "<error>")


def get_ahead_behind(path="."):
    """
    Returns (ahead, behind) commit counts relative to remote.
    Returns (-1, -1) on failure or when not applicable.
    """
    try:
        repo = Repo(path)
        ahead = behind = -1
        tracking_branch = repo.active_branch.tracking_branch()
        if tracking_branch:
            commits_behind = repo.iter_commits(f"{repo.active_branch.name}..{tracking_branch}")
            commits_ahead = repo.iter_commits(f"{tracking_branch}..{repo.active_branch.name}")
            ahead = sum(1 for _ in commits_ahead)
            behind = sum(1 for _ in commits_behind)
        return ahead, behind
    except (AttributeError, exc.GitCommandError, TypeError, exc.InvalidGitRepositoryError) as e:
        logger.debug(f"get_ahead_behind: check skipped (expected in some repos/states): {e}")
        return -1, -1
    except Exception as e:
        logger.error(f"Unexpected error in get_ahead_behind: {e}", exc_info=True)
        return -1, -1


def get_remote_branch_name(branch):
    """
    Get the remote tracking branch name for the given local branch.
    """
    try:
        repo = Repo(".")
        tracking_branch = repo.active_branch.tracking_branch()
        return tracking_branch.name if tracking_branch else "<no remote>"
    except (AttributeError, exc.GitCommandError, exc.InvalidGitRepositoryError) as e:
        logger.debug(f"get_remote_branch_name: failed: {e}")
        return "<no remote>"
    except Exception as e:
        logger.error(f"Unexpected error in get_remote_branch_name: {e}", exc_info=True)
        return "<no remote>"


def get_tracking_branch():
    """Get the tracking branch for current branch."""
    try:
        repo = Repo(".")
        branch = repo.active_branch
        tracking = branch.tracking_branch()
        if tracking:
            return tracking.name  # e.g. 'origin/main'
    except (AttributeError, exc.GitCommandError, exc.InvalidGitRepositoryError) as e:
        logger.debug(f"get_tracking_branch: failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_tracking_branch: {e}", exc_info=True)
    return None