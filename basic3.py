import curses
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
            curses.napms(500)  # 500ms delay

def part_b_live_output(window, command):
    """Run a command and display live output in Part B."""
    h, w = window.getmaxyx()
    try:
        # Start the command process
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        # Stream output live
        for line in process.stdout:
            window.addstr(line)
            window.refresh()
        
        # Check for errors
        for error_line in process.stderr:
            window.addstr(error_line)
            window.refresh()

        # Ensure the process finishes
        process.wait()
    except Exception as e:
        window.addstr(f"Error running command: {e}\n")
        window.refresh()

def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    h, w = stdscr.getmaxyx()
    
    # Create windows for Part A and Part B
    part_a_height = h // 2
    part_a = stdscr.subwin(part_a_height, w, 0, 0)
    part_b = stdscr.subwin(h - part_a_height - 1, w, part_a_height + 1, 0)
    
    # Draw divider
    stdscr.hline(part_a_height, 0, "-", w)
    stdscr.refresh()
    
    # Replace with the actual command you want to run
    command = "git push -v"
    
    # Run Part A and Part B concurrently
    t1 = threading.Thread(target=part_a_animation, args=(part_a,), daemon=True)
    t2 = threading.Thread(target=part_b_live_output, args=(part_b, command))
    
    t1.start()
    t2.start()
    
    # Wait for Part B to finish
    t2.join()

    # Keep the animation running for a few seconds (to demonstrate Part A)
    curses.napms(5000)

if __name__ == "__main__":
    curses.wrapper(main)
