# app.py
import argparse
import ui
from commands import status

def main():
    parser = argparse.ArgumentParser(description="Educational Git Visualizer")
    parser.add_argument("command", choices=["status"])
    args = parser.parse_args()

    command_map = {
        "status": status.run,
    }

    ui.start_curses(command_map[args.command])

if __name__ == "__main__":
    main()
