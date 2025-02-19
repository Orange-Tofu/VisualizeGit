import curses
import threading
import subprocess
import sys
import time

def draw_box(win, y, x, color, title, symbols):
    """Draws a colored box with a title and symbols inside."""
    height, width = 6, 14  # Box dimensions
    max_y, max_x = win.getmaxyx()
    
    # Ensure box fits within window
    if y + height >= max_y or x + width >= max_x:
        return  
    
    win.attron(curses.color_pair(color))
    win.addstr(y, x + (width - len(title)) // 2, title[:width-2])  # Title centered
    
    # Draw box
    win.addstr(y + 1, x, "┌" + "─" * (width - 2) + "┐")
    for i in range(2, height):
        win.addstr(y + i, x, "│" + " " * (width - 2) + "│")
    win.addstr(y + height, x, "└" + "─" * (width - 2) + "┘")
    
    # Place symbols inside the box
    for sy, sx, sym in symbols:
        if 0 <= sy < height and 0 <= sx < width:
            win.addstr(y + sy, x + sx, sym)
    
    win.attroff(curses.color_pair(color))

def display_status(stdscr, stop_event):
    curses.curs_set(0)
    curses.start_color()
    
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    while not stop_event.is_set():
        stdscr.clear()
        draw_box(stdscr, 2, 5, 1, "Untracked", [(2, 5, "•"), (3, 4, "•"), (3, 6, "•")])
        draw_box(stdscr, 2, 25, 2, "Staged", [(3, 6, "•")])
        draw_box(stdscr, 2, 45, 3, "Committed", [(3, 6, "#")])
        draw_box(stdscr, 2, 65, 4, "Origin", [(3, 4, "•"), (3, 6, "#")])
        stdscr.refresh()
        curses.napms(500)  # Sleep for 500ms

def part_a_animation(window, lock, stop_event):
    while not stop_event.is_set():
        with lock:
            display_status(window, stop_event)
        time.sleep(0.5)  # Reduce refresh rate

def part_b_live_output(window, command, output_storage, lock, stop_event):
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        for line in process.stdout:
            with lock:
                max_x = window.getmaxyx()[1] - 1
                window.addstr(line[:max_x])  # Truncate to avoid overflow
                window.refresh()
            output_storage.append(line)
        for error_line in process.stderr:
            with lock:
                max_x = window.getmaxyx()[1] - 1
                window.addstr(error_line[:max_x])
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
    
    part_a_height = max(5, h // 4)  # Ensure part_a has minimum height
    part_a = stdscr.subwin(part_a_height, w, 0, 0)
    part_b = stdscr.subwin(h - part_a_height - 1, w, part_a_height + 1, 0)
    
    stdscr.hline(part_a_height, 0, "-", w)
    stdscr.refresh()
    
    command = "git status"
    output_storage = []
    lock = threading.Lock()
    stop_event = threading.Event()
    
    t1 = threading.Thread(target=part_a_animation, args=(part_a, lock, stop_event), daemon=True)
    t2 = threading.Thread(target=part_b_live_output, args=(part_b, command, output_storage, lock, stop_event))
    
    t1.start()
    t2.start()
    
    t2.join()
    stop_event.set()
    t1.join()
    
    time.sleep(2)
    for line in output_storage:
        sys.stdout.write(line)

if __name__ == "__main__":
    curses.wrapper(main)
