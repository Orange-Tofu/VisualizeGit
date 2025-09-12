# core/git_model.py

class GitState:
    def __init__(self, staged, changed, untracked, branch, ahead=0, behind=0):
        self.staged = staged
        self.changed = changed
        self.untracked = untracked
        self.branch = branch
        self.ahead = ahead
        self.behind = behind
        self.commit_message = None
        self.commit_hashes = []
        self.commit_messages = []
