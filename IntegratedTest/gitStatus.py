import curses
import threading
import subprocess
import sys
import time

from status import gitStatus as statusAnimation  # Assuming status.py contains display_status()

def part_a_animation(window, lock, stop_event):
    """Runs the git status visualization."""
    while not stop_event.is_set():
        with lock:
            window.clear()  # Clear before updating
            statusAnimation.display_status(window, stop_event)  
            window.refresh()
        time.sleep(0.5)  # Reduce refresh rate to avoid conflicts

def part_b_live_output(window, command, output_storage, lock, stop_event):
    """Runs git command and updates the screen with live output."""
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        
        for line in process.stdout:
            with lock:
                window.addstr(line)
                window.refresh()
            output_storage.append(line)
        
        for error_line in process.stderr:
            with lock:
                window.addstr(error_line)
                window.refresh()
            output_storage.append(error_line)

        process.wait()
    except Exception as e:
        with lock:
            window.addstr(f"Error: {e}\n")
            window.refresh()
        output_storage.append(f"Error: {e}\n")
    finally:
        stop_event.set()  # Stop Part A once Part B is done

def main(stdscr):
    curses.curs_set(0)  
    h, w = stdscr.getmaxyx()
    
    part_a_height = h // 4
    part_a = stdscr.subwin(part_a_height, w, 0, 0)
    part_b = stdscr.subwin(h - part_a_height - 1, w, part_a_height + 1, 0)
    
    stdscr.hline(part_a_height, 0, "-", w)
    stdscr.refresh()
    
    command = "git status -v"

    output_storage = []
    lock = threading.Lock()
    stop_event = threading.Event()
    
    t1 = threading.Thread(target=part_a_animation, args=(part_a, lock, stop_event), daemon=True)
    t2 = threading.Thread(target=part_b_live_output, args=(part_b, command, output_storage, lock, stop_event))
    
    t1.start()
    t2.start()
    
    t2.join()
    stop_event.set()  # Ensure animation stops even if thread hasn't exited
    t1.join()

    time.sleep(2)
    for line in output_storage:
        sys.stdout.write(line)

if __name__ == "__main__":
    curses.wrapper(main)
