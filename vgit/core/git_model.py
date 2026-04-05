# core/git_model.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GitState:
    """Represents the core Git repository data for visualization."""
    staged: int
    changed: int
    untracked: int
    branch: str
    ahead: int = 0
    behind: int = 0
    commit_message: Optional[str] = None
    commit_hashes: List[str] = field(default_factory=list)
    commit_messages: List[str] = field(default_factory=list)
    remote_branch: Optional[str] = None
    tracking_branch: Optional[str] = None
    speed: str = 'normal'
    commit_type: str = 'commit_m'
    initial_commit_count: int = -1
    base_hashes: List[str] = field(default_factory=list)
    base_messages: List[str] = field(default_factory=list)
    push_type: str = 'normal'
    pull_type: str = 'normal'  # 'normal', 'ff', 'merge', 'rebase', 'conflict', 'up_to_date', 'error'
    is_rebase: bool = False
    runner: Optional[object] = None
