# vgit — Task Backlog

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
- [ ] Remove `colorama` from `pyproject.toml` and `requirements.txt`
- [ ] Remove `termcolor` from `pyproject.toml` and `requirements.txt`
- [ ] Remove `tqdm` from `pyproject.toml` and `requirements.txt`
- [ ] Remove `Pygments` from `pyproject.toml` and `requirements.txt`
- [ ] Remove `markdown-it-py` and `mdurl` from `pyproject.toml` and `requirements.txt`
- [ ] Remove `windows-curses` from `pyproject.toml` and `requirements.txt`
- [ ] Add `rich` as a dependency
- [ ] Add `click` or `typer` as a dependency
- [ ] Run `pip install .` in a clean venv and verify no import errors

---

## Phase 2: Quick Wins (framework-agnostic fixes, do alongside or after Phase 1)

### 2.1 Replace hardcoded `time.sleep(5)` with event-driven lifecycle
- [ ] Animation should keep looping while the command subprocess is running
- [ ] On command completion, play final frame(s) and stop — no arbitrary sleep
- [ ] Add a short configurable post-completion pause (1–2s), not a fixed 5s

### 2.2 Replace bare `except Exception: pass`
- [ ] Catch specific exceptions only (not broad `Exception`)
- [ ] Log unexpected errors to a debug log file (e.g., `~/.vgit/debug.log`)
- [ ] Keep existing fallback behavior (don't crash) but make failures diagnosable

### 2.3 Convert `GitState` to a dataclass
- [ ] Add `from dataclasses import dataclass, field` to `git_model.py`
- [ ] Define all fields explicitly (including `commit_type`, `commit_message`, etc.)
- [ ] Move animation-specific state (`_frame`, `_fetch_stage`) out of `GitState` into animation modules
- [ ] Update all consumers to use the new dataclass

### 2.4 Refactor duplicated code
- [ ] Extract shared `draw_box()` into a `animations/widgets.py` module
- [ ] Extract `-m` / `--message` parsing in `commands/commit.py` into a helper function
- [ ] Consolidate `Repo(".")` instantiation — pass a single `Repo` instance through the call chain

### 2.5 Delete or fix `examples/app.py`
- [ ] Decide: archive for reference or delete entirely
- [ ] If keeping, fix imports to use `vgit.` package prefix
- [ ] If deleting, remove the `examples/` directory

---

## Phase 3: New Command Animations

### 3.1 Correct Git Commit animation (P0)
- [ ] Identify visual discontinuities in the current commit animation.
- [ ] Ensure the animated commit node properly attaches to the local branch line.
- [ ] Verify both `commit -m` and `commit --amend` visual logic.

### 3.2 Add continuous animation loop (P0)
- [ ] Change animation to loop continuously.
- [ ] Wait for user input (e.g., key press like 'q' or 'Enter') to exit the UI.
- [ ] Update documentation to reflect the new exit condition.

### 3.3 `vgit push` (P0)
- [ ] Design animation: commits flying from local branch to remote (mirror of fetch)
- [ ] Create `animations/push.py` with `render()` and `start()`
- [ ] Create `commands/push.py` — build state, start animation, run `git push`, stop
- [ ] Register `"push"` in command registry
- [ ] Handle edge cases: no remote, force push, rejected push

### 3.4 `vgit pull` (P0)
- [ ] Design animation: fetch phase (commits arriving) + merge phase (branches converging)
- [ ] Create `animations/pull.py`
- [ ] Create `commands/pull.py` — may need to show two-stage animation
- [ ] Register `"pull"` in command registry
- [ ] Handle fast-forward vs merge commit cases

### 3.5 `vgit add` (P1)
- [ ] Design animation: files moving from "Changed"/"Untracked" box to "Staged" box
- [ ] Create `animations/add.py`
- [ ] Create `commands/add.py`
- [ ] Register `"add"` in command registry
- [ ] Support `vgit add .` and `vgit add <file>`

### 3.6 `vgit checkout` / `vgit switch` (P1)
- [ ] Design animation: HEAD pointer moving between branches
- [ ] Create `animations/checkout.py`
- [ ] Create `commands/checkout.py`
- [ ] Register both `"checkout"` and `"switch"` in command registry
- [ ] Handle branch creation (`-b` flag)

### 3.7 `vgit merge` (P2)
- [ ] Design animation: two branch lines converging into a merge commit
- [ ] Create `animations/merge.py`
- [ ] Create `commands/merge.py`
- [ ] Register `"merge"` in command registry
- [ ] Handle fast-forward vs three-way merge
- [ ] Handle merge conflicts (show conflict state)

### 3.8 `vgit rebase` (P2)
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
| 2026-03-15 | Initial backlog created from full project analysis |
| 2026-03-15 | Reordered: migration (Phase 1) before curses-specific fixes; dropped obsolete curses bug tasks |
