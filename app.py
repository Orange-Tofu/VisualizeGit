# app.py
import argparse
import ui
from commands import status
import core.ui_utils as ui_utils
import curses

def main(stdscr):
    ui_utils.check_terminal_size(stdscr)
    
    parser = argparse.ArgumentParser(description="Educational Git Visualizer")
    parser.add_argument("command", choices=["status"])
    args = parser.parse_args()

    command_map = {
        "status": status.run,
    }

    ui.start_curses(command_map[args.command])

if __name__ == "__main__":
    import sys
    curses.wrapper(main)
