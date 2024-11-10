import sys
import subprocess
import time
from rich.progress import track
from rich.console import Console

console = Console()

def run_git_command(command):
    """Runs the actual Git command and prints the output."""
    try:
        # Run the command and capture the output
        result = subprocess.run(["git"] + command, check=True, text=True, capture_output=True)
        console.print(result.stdout)
        console.print(result.stderr, style="red")
    except subprocess.CalledProcessError as e:
        console.print(e.stderr, style="red")

def show_push_animation():
    """Simulates a 'pushing files' animation."""
    console.print("\n[bold green]Pushing files to remote repository...[/bold green]")
    for step in track(range(100), description="Uploading..."):
        time.sleep(0.05)  # This creates the animation effect

def main():
    if len(sys.argv) < 2:
        console.print("[red]Error:[/red] Please specify a git command (e.g., 'push').")
        return

    # Parse the vgit command
    git_command = sys.argv[1]
    git_args = sys.argv[2:]

    if git_command == "push":
        show_push_animation()  # Display animation
        run_git_command([git_command] + git_args)  # Run actual git command
    else:
        # For other git commands, just call them directly
        run_git_command([git_command] + git_args)

if __name__ == "__main__":
    main()
