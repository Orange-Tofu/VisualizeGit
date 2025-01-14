import curses
import time
import threading
import subprocess

def part_a_animation(window):
    """Display ASCII animation in Part A."""
    frames = [
        r"  (o_o) ",
        r"  (<_<) ",
        r"  (>_>) ",
    ]
    h, w = window.getmaxyx()
    while True:
        for frame in frames:
            window.clear()
            window.addstr(1, w // 2 - len(frame) // 2, frame)
            window.refresh()
            time.sleep(0.5)

def part_b_command_output(window):
    """Run and display the output of a mock `sftp` command."""
    h, w = window.getmaxyx()
    # Mock the `sftp` output
    mock_output = ["Connecting to server...", "Connection established.", "Directory listing:", "- file1.txt", "- file2.txt"]
    for line in mock_output:
        window.addstr(line + "\n")
        window.refresh()
        time.sleep(1)

def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    h, w = stdscr.getmaxyx()
    
    # Create windows for Part A and Part B
    part_a_height = h // 3
    part_a = stdscr.subwin(part_a_height, w, 0, 0)
    part_b = stdscr.subwin(h - part_a_height - 1, w, part_a_height + 1, 0)
    
    # Draw divider
    stdscr.hline(part_a_height, 0, "-", w)
    stdscr.refresh()
    
    # Run Part A and Part B concurrently
    t1 = threading.Thread(target=part_a_animation, args=(part_a,), daemon=True)
    t2 = threading.Thread(target=part_b_command_output, args=(part_b,))
    
    t1.start()
    t2.start()
    
    # Wait for Part B to finish (simulating the command running)
    t2.join()

    # Keep the animation running for a few seconds (to demonstrate Part A)
    time.sleep(5)

if __name__ == "__main__":
    curses.wrapper(main)
