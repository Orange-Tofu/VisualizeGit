+# vgit — Task Backlog

> Pick tasks top-down. Each top-level item is an independent work unit.
> Mark `[/]` when in-progress, `[x]` when done.

---

## Phase 1: Framework Migration (eliminates curses/threading bugs by design)

> Migrating to `rich` + `asyncio` + `click`/`typer` removes the need to fix curses-specific issues
> (triple `curses.wrapper`, thread safety, `windows-curses` dependency) — they vanish with the old framework.

### 1.1 Migrate TUI from `curses` to `rich`
- [x] Evaluate `rich.Live` + `rich.Layout` as replacement for manual curses split-screen
- [x] Replace `animations/base.py` animation loop with `rich.Live` context manager
- [x] Replace `core/runner.py` curses writes with `rich.Console` output
- [x] Update `ui.py` — replace `setup_windows()` and `start_curses()` with rich-based equivalents
- [x] Port `animations/status.py` to rich `Table` / `Panel` widgets
- [x] Port `animations/fetch.py` to rich
- [x] Port `animations/commit.py` to rich
- [x] Port `animations/default.py` to rich
- [x] Remove `windows-curses` dependency
- [x] Remove `curses` imports from all modules
- [x] Verify on Windows.
- [x] Update `ui_config.py` — replace curses color pairs with rich style strings


### 1.2 Migrate from threads to `asyncio`
- [x] Convert `CommandRunner.run_and_stream()` to use `asyncio.create_subprocess_exec`
- [x] Convert animation loop to an async task instead of a daemon thread
- [x] Use `asyncio.gather()` to run animation + command concurrently
- [x] Remove `AnimationController` thread-join logic — use `asyncio.Task.cancel()` instead
- [x] Update all command handlers (`status.py`, `fetch.py`, `commit.py`) to be `async def run()`
- [x] Remove `threading` imports from all modules


### 1.3 Migrate from `argparse` to `click` or `typer`
- [x] Choose between `click` (mature, explicit) and `typer` (type-hint driven, built on click)
- [x] Create a CLI group: `vgit` as the top-level command
- [x] Register each supported command
- [x] Support pass-through of unknown flags to the underlying `git` command
- [x] Add `--speed` option (`fast` / `normal` / `slow`)
- [x] Remove `argparse` from `cli.py`
- [x] Ensure arg parsing happens *before* TUI init (clean `--help` and error output)

### 1.4 Clean up dependencies
- [x] Remove `colorama` from `pyproject.toml` and `requirements.txt`
- [x] Remove `termcolor` from `pyproject.toml` and `requirements.txt`
- [x] Remove `tqdm` from `pyproject.toml` and `requirements.txt`
- [x] Remove `Pygments` from `pyproject.toml` and `requirements.txt`
- [x] Remove `markdown-it-py` and `mdurl` from `pyproject.toml` and `requirements.txt`
- [x] Remove `windows-curses` from `pyproject.toml` and `requirements.txt`
- [x] Add `rich` as a dependency
- [x] Add `click` or `typer` as a dependency
- [x] Ensure `requirements.txt` and `pyproject.toml` are updated with correct dependencies and versions.
- [x] Run `pip install .` in a clean venv and verify no import errors

---

## Phase 2: Quick Wins (framework-agnostic fixes, do alongside or after Phase 1)

### 2.1 Add continuous animation loop with user-input exit (promoted from 3.2)
> `time.sleep` is gone — `asyncio.sleep(pause)` with speed-scaled values replaced it in Phase 1.
> Implementing this task (loop until keypress) is the correct event-driven successor.
- [x] Change animation to loop continuously after the git command finishes
- [x] Wait for user input (e.g., key press like `q` or `Enter`) to exit the UI instead of a fixed sleep
- [x] Update all command handlers (`status.py`, `fetch.py`, `commit.py`) to await the keypress signal
- [x] Update documentation / help text to reflect the new exit condition

### 2.2 Replace bare `except Exception: pass` [x]
- [x] Catch specific exceptions only (not broad `Exception`)
- [x] Log unexpected errors to a debug log file (e.g., `~/.vgit/debug.log`)
- [x] Keep existing fallback behavior (don't crash) but make failures diagnosable

### 2.3 Convert `GitState` to a dataclass [x]
- [x] Add `from dataclasses import dataclass, field` to `git_model.py`
- [x] Define all fields explicitly (including `commit_type`, `commit_message`, etc.)
- [x] Move animation-specific state (`_frame`, `_fetch_stage`) out of `GitState` into animation modules
- [x] Update all consumers to use the new dataclass

### 2.4 Refactor duplicated code [x]
- [x] Extract shared `draw_box()` into a `animations/widgets.py` module
- [x] Extract `-m` / `--message` parsing in `commands/commit.py` into a helper function
- [x] Consolidate `Repo(".")` instantiation — pass a single `Repo` instance through the call chain

### 2.5 Delete or fix `examples/app.py` [x]
- [x] Decide: archive for reference or delete entirely (deleted)
- [x] If keeping, fix imports to use `vgit.` package prefix
- [x] If deleting, remove the `examples/` directory

---

## Phase 3: New Command Animations

### 3.1 Correct and Verify all Existing Git commands (P0)
- [x] Git status
- [x] Git fetch
- [x] Git commit
- [x] Unsupported versions of supported commamnds
- [x] Unsupported commands

### 3.2 `vgit push` (P0)
- [x] Design Core Animation: commits flying from local branch up to remote (mirror of fetch)
- [x] Create `animations/push.py` with `render()` and `start()`
- [x] Create `commands/push.py` — build state, start animation, run `git push`, stop
- [x] Register `"push"` in command registry
- [x] Visual Caveat: Push Rejected (Non-Fast-Forward) — animate bounce-back/barrier and show error text
- [x] Visual Caveat: Force Push (`--force`) — animate aggressive flying commit knocking off remote commits
- [x] Visual Caveat: No Upstream Branch — animate the spawning/creation of the remote branch dynamically
- [x] Visual Caveat: Everything Up-To-Date — show a green checkmark instantly instead of flying commits
- [x] Visual Caveat: Pushing Multiple Commits — animate a "train" of consecutive commits based on `ahead` count

### 3.3 `vgit pull` (P0)
- [x] Design animation: fetch phase (commits arriving) + integration phase (3-way merge, rebase, or FF)
- [x] Create `animations/pull.py` — handle stages: `fetching`, `evaluating`, `merging`, `rebasing`, `colliding`
- [x] Create `commands/pull.py` — detect `--rebase`, ahead/behind, tracking branch
- [x] Register `"pull"` in `vgit/cli.py`
- [x] Visual: Standard 3-Way Merge (diverging branches + merge node)
- [x] Visual: Rebase (detaching and replaying commits)
- [x] Visual: Fast-Forward (simple append)
- [x] Visual: Conflict (commit collision animation + halt)
- [x] Visual: Up-To-Date (instant checkmark)
- [x] Visual: Missing Upstream (error banner).

### 3.4 `vgit add` (P1)
- [x] Design animation: files moving from "Changed"/"Untracked" box to "Staged" box
- [x] Create `animations/add.py`
- [x] Create `commands/add.py`
- [x] Register `"add"` in command registry
- [x] Support `vgit add .` and `vgit add <file>`

### 3.5 `vgit checkout` / `vgit switch` (P1)
- [x] Design animation: HEAD pointer moving between branches
- [x] Create `animations/checkout.py`
- [x] Create `commands/checkout.py` and `commands/branch.py` (for deletion)
- [x] Register `"checkout"`, `"switch"`, and `"branch"` in command registry
- [x] Handle branch creation (`-b` flag) and deletion (`-d` / `-D` flags)

### 3.6 `vgit merge` (P2)
- [x] Design animation: two branch lines converging into a merge commit
- [x] Create `animations/merge.py`
- [x] Create `commands/merge.py`
- [x] Register `"merge"` in command registry
- [x] Handle fast-forward vs three-way merge
- [x] Handle merge conflicts (show conflict state)
- [] Need to add git squash, abort and also refine visualization for 3-way merge. 

### 3.7 `vgit rebase` (P2)
- [ ] Design animation: commits being replayed on top of another branch
- [ ] Create `animations/rebase.py`
- [ ] Create `commands/rebase.py`
- [ ] Register `"rebase"` in command registry

---

## Phase 4: Code Quality & Testing

### 4.1 Add unit tests
- [ ] Set up `pytest` in `pyproject.toml` (add `[project.optional-dependencies]` for dev)
- [ ] Create `tests/` directory with `conftest.py`
- [ ] Test `core/git_utils.py` — mock `GitPython.Repo` to test `build_state()`, `get_ahead_behind()`
- [ ] Test `core/git_model.py` — verify `GitState` construction and defaults
- [ ] Test CLI argument parsing — verify subcommand dispatch, edge cases
- [ ] Test `commands/commit.py` — verify `-m`, `--amend`, `--no-edit` flag parsing

### 4.2 Add CI pipeline
- [ ] Create `.github/workflows/ci.yml`
- [ ] Run `pytest` on push/PR
- [ ] Run linter (`ruff`) on push/PR
- [ ] Verify `pip install .` succeeds in CI
- [ ] Test on Python 3.8, 3.10, 3.12

### 4.3 Add logging
- [ ] Create a `core/logger.py` module with a configured `logging.Logger`
- [ ] Replace all `print()` statements with logger calls
- [ ] Add `--verbose` / `--debug` CLI flag to control log level
- [ ] Log to `~/.vgit/debug.log` when debug mode is on

---

## Phase 5: Polish & UX

### 5.1 Terminal resize handling
- [ ] Detect terminal resize events
- [ ] Recalculate layout and redraw on resize
- [ ] Show friendly error if resized below minimum dimensions

### 5.2 Graceful exit & output replay
- [ ] On command completion, show a brief "Done" status in the animation pane
- [ ] On exit, cleanly restore the terminal and reprint the captured git output
- [ ] Handle `Ctrl+C` (SIGINT) gracefully — stop animation, kill subprocess, restore terminal

### 5.3 Plugin / registry pattern for commands
- [ ] Create a `@register_command("name")` decorator
- [ ] Auto-discover command modules in `commands/` package
- [ ] Remove hardcoded command dispatch dict from CLI

### 5.4 Color theme support
- [ ] Define a `Theme` dataclass with color mappings
- [ ] Provide at least `dark` and `light` presets
- [ ] Add `--theme` CLI flag
- [ ] Store user preference in `~/.vgit/config`

---

## Changelog

| Date | Change |
|---|---|
| 2026-05-26 | Implemented task 3.6 (`vgit merge`): designed Fast-Forward, 3-Way Merge, and Merge Conflict animations; created `vgit/commands/merge.py` and `vgit/animations/merge.py`; registered command in CLI. |
| 2026-04-06 | Implemented task 3.5 (`vgit checkout` / `switch`): created shared animation for branch switching and added `vgit branch -d` deletion animation support. |
| 2026-04-05 | Implemented task 3.4 (`vgit add`): created animation showing files moving from 'Unstaged' to 'Staged' areas with a scrolling 'trail' icon effect. |
| 2026-03-23 | Successfully implemented fallback for all unknown Git commands: using a custom `CatchAllGroup`, `vgit <cmd>` now consistently launches the TUI with the 'unsupported' animation. |
| 2026-03-23 | Added commit success detection: use `initial_commit_count` to ensure new commit hash only displays if command succeeds; otherwise show placeholder `(........)` and failure note. |
| 2026-03-23 | Fixed commit animation alignment: introduced line-synchronization to prevent horizontal drift when messages are longer than hashes; preserved 3-segment arrows and precise vertical alignment. |
| 2026-03-23 | Fixed Rich layout placeholder glitch: initialized panes with empty Panels to preserve box borders while hiding debug placeholders (e.g. `Layout(name='bottom')`) when commands have no output. |
| 2026-03-21 | Phase 2 audit: 2.1 (time.sleep) superseded — asyncio migration eliminated it; replaced with continuous loop task promoted from 3.2. Phase 3 tasks renumbered (3.2→removed, 3.3→3.2, etc.). |
| 2026-03-20 | Completed Phase 1 (Rich migration, asyncio refactor, Click CLI); added commit animation and looping tasks to Phase 3. |
| 2026-03-15 | Initial backlog created from full project analysis |
| 2026-03-15 | Reordered: migration (Phase 1) before curses-specific fixes; dropped obsolete curses bug tasks |
