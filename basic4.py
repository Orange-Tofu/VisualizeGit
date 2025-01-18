import curses
import threading
import subprocess
import time
import sys
import os

def part_a_animation(window, lock, stop_event):
    """Display ASCII animation in Part A."""
    frames = [
        r"  (o_o) ",
        r"  (<_<) ",
        r"  (>_>) ",
    ]
    h, w = window.getmaxyx()
    while not stop_event.is_set():
        for frame in frames:
            if stop_event.is_set():
                break
            with lock:
                window.clear()
                window.addstr(1, w // 2 - len(frame) // 2, frame)
                window.refresh()
            curses.napms(500)  # 500ms delay

def part_b_live_output(window, command, output_storage, lock, stop_event):
    """Run a command and display live output in Part B while storing it."""
    h, w = window.getmaxyx()
    try:
        # Start the command process with unbuffered output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        # Stream output live and save it
        for line in process.stdout:
            with lock:
                window.addstr(line)
                window.refresh()
            output_storage.append(line)  # Save to storage
        
        # Stream and save error output
        for error_line in process.stderr:
            with lock:
                window.addstr(error_line)
                window.refresh()
            output_storage.append(error_line)  # Save to storage

        # Ensure the process finishes
        process.wait()
    except Exception as e:
        error_message = f"Error running command: {e}\n"
        with lock:
            window.addstr(error_message)
            window.refresh()
        output_storage.append(error_message)
    finally:
        stop_event.set()  # Signal animation to stop

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
    # command = "ping -c 5 google.com" if not subprocess.os.name == "nt" else "ping -n 5 google.com"
    command = "git add ."
    
    # Storage for command output
    output_storage = []
    
    # Lock for synchronizing window writes
    lock = threading.Lock()
    
    # Event to signal when Part B is done
    stop_event = threading.Event()
    
    # Run Part A and Part B concurrently
    t1 = threading.Thread(target=part_a_animation, args=(part_a, lock, stop_event), daemon=True)
    t2 = threading.Thread(target=part_b_live_output, args=(part_b, command, output_storage, lock, stop_event))
    
    t1.start()
    t2.start()
    
    t2.join()
    t1.join()  # Wait for animation thread to finish
    time.sleep(2)
    
    for line in output_storage:
        sys.stdout.write(line)
        sys.stdout.flush()

if __name__ == "__main__":
    curses.wrapper(main)
