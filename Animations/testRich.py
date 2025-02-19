from rich.console import Console
from rich.progress import track
import time

console = Console()

def animate():
    for i in track(range(10), description="Processing..."):
        console.print(f"Step {i+1} out of 10", style="bold magenta")
        time.sleep(0.5)

animate()
