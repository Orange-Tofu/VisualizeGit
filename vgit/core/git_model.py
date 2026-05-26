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
    add_status: str = 'running' # 'running', 'success', 'failed'
    to_add_count: int = 0
    initial_staged: int = 0
    initial_unstaged: int = 0
    target_branch: Optional[str] = None
    is_new_branch: bool = False
    is_detached_head: bool = False
    checkout_type: str = 'branch' # 'branch', 'delete_branch', 'unsupported'
    delete_branch_name: Optional[str] = None
    upstream_ref: Optional[str] = None
    checkout_status: str = 'running' # 'running', 'success', 'failed'
    merge_type: str = 'merge'  # 'merge', 'ff', 'collision', 'up_to_date', 'error'
    is_no_ff: bool = False
    target_hashes: List[str] = field(default_factory=list)
    target_messages: List[str] = field(default_factory=list)
