import shutil
import sys
from vgit.core import ui_config as cfg

def check_terminal_size():
    """
    Ensure the terminal has enough rows/cols for our UI layout.
    If not, print a friendly warning (or exit if strictly needed).
    """
    cols, rows = shutil.get_terminal_size()

    if rows < cfg.MIN_TERMINAL_HEIGHT or cols < cfg.MIN_TERMINAL_WIDTH:
        print(
            f"❌ Terminal too small: {cols}x{rows} "
            f"(minimum {cfg.MIN_TERMINAL_WIDTH}x{cfg.MIN_TERMINAL_HEIGHT} recommended).\n"
            "👉 Please maximize your terminal."
        )
        sys.exit(1)
