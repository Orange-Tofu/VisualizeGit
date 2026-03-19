# vgit/cli.py

import argparse
import asyncio
from vgit import ui
from vgit.commands import status, fetch, commit

SUPPORTED_COMMANDS = {
    "status": status.run,
    "fetch": fetch.run,
    "commit": commit.run
}

def main():
    """No-arg function for pip entry point"""
    parser = argparse.ArgumentParser(description="Educational Git Visualizer")
    parser.add_argument("git_command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not args.git_command:
        print("Please provide a git command, e.g. `vgit status -sb`")
        import sys
        sys.exit(1)

    subcommand = args.git_command[0]
    full_command = ["git"] + args.git_command

    animation_fn = SUPPORTED_COMMANDS.get(subcommand, ui.unsupported_command_animation)
    asyncio.run(ui.start_ui(animation_fn, full_command))

