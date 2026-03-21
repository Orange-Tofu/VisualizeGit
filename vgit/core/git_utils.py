from git import Repo, exc
from vgit.core.git_model import GitState
from vgit.core.logger import logger

def build_state(path=".", repo=None):
    """Safely construct the GitState. Reuses repo if provided, else creates one."""
    try:
        r = repo or Repo(path)
        staged = 0
        try:
             # This might fail on new repos with no commits
             staged = sum(1 for _ in r.index.diff("HEAD"))
        except (exc.GitCommandError, exc.BadName):
             # For a fresh repo, maybe check if something is added to the index?
             # But usually HEAD exists.
             pass
             
        changed = sum(1 for _ in r.index.diff(None))
        untracked = len(r.untracked_files)
        branch = ""
        try:
            branch = r.active_branch.name
        except (TypeError, AttributeError, exc.GitCommandError):
             branch = "Detached / Initial"

        return GitState(staged, changed, untracked, branch)
    except (exc.InvalidGitRepositoryError, exc.NoSuchPathError, NameError, AttributeError) as e:
        logger.debug(f"build_state: failed (likely no repo): {e}")
        return GitState(0, 0, 0, "<no branch>")
    except Exception as e:
        logger.error(f"Unexpected error in build_state: {e}", exc_info=True)
        return GitState(0, 0, 0, "<error>")


def get_ahead_behind(path=".", repo=None):
    """Returns (ahead, behind) counts. Reuses repo if provided."""
    try:
        r = repo or Repo(path)
        ahead = behind = -1
        try:
            tracking_branch = r.active_branch.tracking_branch()
            if tracking_branch:
                behind_commits = r.iter_commits(f"{r.active_branch.name}..{tracking_branch}")
                ahead_commits = r.iter_commits(f"{tracking_branch}..{r.active_branch.name}")
                ahead = sum(1 for _ in ahead_commits)
                behind = sum(1 for _ in behind_commits)
        except (AttributeError, exc.GitCommandError, TypeError):
             pass
        return ahead, behind
    except (exc.InvalidGitRepositoryError, exc.NoSuchPathError) as e:
        logger.debug(f"get_ahead_behind: failed: {e}")
        return -1, -1
    except Exception as e:
        logger.error(f"Unexpected error in get_ahead_behind: {e}", exc_info=True)
        return -1, -1


def get_remote_branch_name(branch_name, repo=None):
    """Gets the remote tracking branch name."""
    try:
        r = repo or Repo(".")
        tracking_branch = r.active_branch.tracking_branch()
        return tracking_branch.name if tracking_branch else "<no remote>"
    except (AttributeError, exc.GitCommandError, exc.InvalidGitRepositoryError):
        return "<no remote>"
    except Exception as e:
        logger.error(f"Unexpected error in get_remote_branch_name: {e}", exc_info=True)
        return "<no remote>"


def get_tracking_branch(repo=None):
    """Gets the tracking branch name."""
    try:
        r = repo or Repo(".")
        tracking = r.active_branch.tracking_branch()
        if tracking:
            return tracking.name
    except (AttributeError, exc.GitCommandError, exc.InvalidGitRepositoryError):
        pass
    except Exception as e:
        logger.error(f"Unexpected error in get_tracking_branch: {e}", exc_info=True)
    return None

def get_commit_message_from_args(args):
    """Helper to extract Git commit message from cli arguments."""
    for opt in ["-m", "--message"]:
        if opt in args:
            idx = args.index(opt)
            if idx + 1 < len(args):
                return args[idx + 1]
    return ""