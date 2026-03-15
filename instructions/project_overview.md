# vgit — Project Overview

> **One-shot gateway document.** If you're a human or AI reading this project for the first time, this file tells you everything you need to know.

---

## What Is vgit?

**vgit** is a free, open-source, terminal-based educational tool that **visualizes Git commands** using ASCII animations. When you run `vgit status` instead of `git status`, you see:

- **Top pane** — An animated visualization of what the Git operation is doing conceptually (e.g., commits flying from remote to local during `fetch`)
- **Bottom pane** — The real `git` command output, streamed in real time

The goal is to help students, educators, and Git newcomers understand what Git is doing under the hood.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python ≥ 3.8 |
| TUI (Terminal UI) | `curses` (`windows-curses` on Windows) |
| Git introspection | `GitPython` (Python bindings for git repos) |
| Packaging | `setuptools` via `pyproject.toml` |
| License | GPL-3.0-or-later |

### Entry Point

```
pip install vgit        # installs the `vgit` CLI command
vgit status             # runs git status with animation
vgit commit -m "msg"    # runs git commit with animation
```

The pip entry point is defined in `pyproject.toml`:
```toml
[project.scripts]
vgit = "vgit.__main__:main"
```

---

## Repository Structure

```
vgit/                          ← project root (pip-installable package root)
├── pyproject.toml             ← build config, dependencies, entry point
├── requirements.txt           ← pinned dev dependencies
├── ReadMe.md                  ← user-facing README
├── LICENSE                    ← GPL-3.0
├── CLA.md                     ← Contributor License Agreement
├── CONTRIBUTING.md            ← Contribution guidelines
├── development-read.txt       ← Internal dev notes & backlog
├── instructions/
│   ├── aim.md                 ← Original vision document (TUI design spec)
│   ├── project_overview.md    ← THIS FILE
│   └── todo.md                ← Prioritized task backlog
│
└── vgit/                      ← Python package
    ├── __init__.py
    ├── __main__.py            ← Entry: curses.wrapper(main)
    ├── cli.py                 ← CLI: argparse, command dispatch
    ├── ui.py                  ← Window setup, start_curses(), fallback handler
    │
    ├── core/                  ← Shared infrastructure
    │   ├── runner.py          ← CommandRunner: subprocess + stream to curses
    │   ├── git_utils.py       ← GitPython wrappers (build_state, ahead/behind)
    │   ├── git_model.py       ← GitState data class
    │   ├── ui_config.py       ← Layout constants (positions, colors, sizes)
    │   └── ui_utils.py        ← Terminal size validation
    │
    ├── animations/            ← TUI renderers (one per Git command)
    │   ├── base.py            ← AnimationController + threaded render loop
    │   ├── status.py          ← 4-box visualization (untracked/changed/staged/committed)
    │   ├── fetch.py           ← Commits flying from remote to local ref
    │   ├── commit.py          ← New commit appearing + amend animation
    │   └── default.py         ← "Not supported" fallback with robot ASCII
    │
    ├── commands/              ← Command orchestrators (wire animation + runner)
    │   ├── status.py          ← build state → start animation → run git → stop
    │   ├── fetch.py           ← same pattern for fetch
    │   └── commit.py          ← handles -m, --amend, --no-edit variants
    │
    └── examples/
        └── app.py             ← Legacy standalone entry (broken imports, pre-packaging)
```

---

## Architecture & Data Flow

```
User runs: vgit commit -m "fix bug"
           │
           ▼
    __main__.py
           │ curses.wrapper(main)
           ▼
    cli.py → argparse → subcommand = "commit"
           │ lookup SUPPORTED_COMMANDS["commit"]
           ▼
    ui.py → setup_windows(stdscr) → top_window, bottom_window
           │ CommandRunner(["git","commit","-m","fix bug"], bottom_window)
           ▼
    commands/commit.py → run(top_window, runner)
           │
           ├─→ git_utils.build_state()         ← GitPython: staged/changed/untracked/branch
           ├─→ Parse -m / --amend flags         ← Determine animation variant
           ├─→ Repo(".").iter_commits()          ← Load last 3 commits for animation
           │
           ├─→ commit_anim.start(top_window, git_state)
           │       └─→ base.start_animation()   ← Spawns daemon thread
           │           └─→ Thread: render() loop every 0.5s
           │
           ├─→ runner.run_and_stream()           ← subprocess.Popen("git commit -m ...")
           │       └─→ Streams stdout → bottom_window line by line
           │
           ├─→ time.sleep(5)                     ← Hardcoded wait (known issue)
           └─→ controller.stop()                 ← Sets stop_event, joins thread
```

### Key Abstractions

| Class/Function | Location | Role |
|---|---|---|
| `AnimationController` | `animations/base.py` | Wraps a stop-event + thread; `.stop()` to halt |
| `start_animation(win, render_fn, state)` | `animations/base.py` | Generic loop: clear → render → refresh → sleep 0.5s |
| `CommandRunner` | `core/runner.py` | Wraps `subprocess.Popen`; streams output to a curses window |
| `GitState` | `core/git_model.py` | Data bag: staged, changed, untracked, branch, ahead, behind |
| `build_state()` | `core/git_utils.py` | Creates `GitState` from current repo via GitPython |

### How to Add a New Command

1. Create `vgit/animations/mycommand.py` — implement `render(window, state)` and `start(window, git_state)`
2. Create `vgit/commands/mycommand.py` — implement `run(top_window, runner)` following the pattern in `status.py`
3. Register in `cli.py` → `SUPPORTED_COMMANDS["mycommand"] = mycommand.run`

---

## Supported Commands

| Command | Animation | Notes |
|---|---|---|
| `vgit status` | 4-box dashboard (untracked, changed, staged, committed with ↑/↓) | Shows ahead/behind from remote |
| `vgit fetch` | Commits flying from remote branch to local ref box | Two-stage: fetching → done |
| `vgit commit -m "msg"` | New commit node slides in, HEAD pointer moves | Shows last 3 commit hashes |
| `vgit commit --amend --no-edit` | Files fly to staging area, then back as replacement commit | Three-stage animation |
| `vgit commit --amend -m "msg"` | Same as above with new message | — |
| `vgit <anything else>` | Robot ASCII + "NOT SUPPORTED" message | Falls back to default animation |

---

## Known Issues & Technical Debt

> These are documented in detail in `instructions/todo.md` and are being addressed incrementally.

1. **Thread safety** — `curses` is not thread-safe; animation thread and command runner write concurrently with no `threading.Lock`
2. **Triple `curses.wrapper()`** — `__main__.py` → `cli.py` → `ui.py` each call `curses.wrapper()`, causing redundant init/teardown
3. **Hardcoded `time.sleep(5)`** — Animation lingers for 5s regardless of command duration
4. **Silent exception swallowing** — `except Exception: pass` hides real bugs
5. **Unused dependencies** — `rich`, `tqdm`, `termcolor`, `colorama`, `Pygments`, `markdown-it-py` are declared but never imported
6. **No tests** — Zero test files exist
7. **Broken `examples/app.py`** — Uses bare `import ui` (pre-packaging relic)
8. **Mutable state bag** — `GitState` gets arbitrary attributes bolted on at runtime
9. **Duplicated code** — `draw_box()` exists in both `animations/status.py` and `animations/fetch.py`; `-m`/`--message` parsing is duplicated in `commands/commit.py`

---

## Development Setup

```bash
git clone https://github.com/Orange-Tofu/VisualizeGit
cd VisualizeGit
pip install -r requirements.txt    # or: pip install -e .
python -m vgit status              # run from source
```

**Requirements**: Python ≥ 3.8, a terminal ≥ 110×30 characters, and a git repository in the current directory.

---

## References

- [aim.md](aim.md) — Original vision document with terminal layout spec
- [todo.md](todo.md) — Current task backlog
- [development-read.txt](../development-read.txt) — Historical dev notes
