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
        stop_event.set()
