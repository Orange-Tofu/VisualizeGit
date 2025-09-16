# core/ui_config.py

import shutil

# Terminal Width and Height
MIN_TERMINAL_HEIGHT = 30
MIN_TERMINAL_WIDTH = 110

# Current terminal size (updated at import, can be refreshed during curses)
_size = shutil.get_terminal_size(fallback=(MIN_TERMINAL_WIDTH, MIN_TERMINAL_HEIGHT))
CURRENT_TERMINAL_WIDTH = _size.columns
CURRENT_TERMINAL_HEIGHT = _size.lines

def update_current_terminal_size(stdscr):
    """Update CURRENT_TERMINAL_WIDTH/HEIGHT from an active curses window."""
    global CURRENT_TERMINAL_WIDTH, CURRENT_TERMINAL_HEIGHT
    try:
        height, width = stdscr.getmaxyx()
        CURRENT_TERMINAL_HEIGHT = height
        CURRENT_TERMINAL_WIDTH = width
    except Exception:
        # If stdscr is invalid, keep existing values
        pass
# Generic UI constants
BOX_HEIGHT = CURRENT_TERMINAL_HEIGHT//7
BOX_WIDTH = CURRENT_TERMINAL_WIDTH//10
ROW_Y = 3

# X positions for git status boxes
if CURRENT_TERMINAL_WIDTH>78:
    SymbolPosX=2
    BOTTOM_ROW_TEXT_Y =10
    SymbolPosY=2
    STATUS_X_POSITIONS = {
    "untracked": (BOX_WIDTH),
    "changed": BOX_WIDTH+20 ,
    "staged": BOX_WIDTH+40,
    "committed": BOX_WIDTH+60,
}
else:
    SymbolPosX=3
    BOTTOM_ROW_TEXT_Y =40
    SymbolPosY=3
    STATUS_X_POSITIONS = {
    "untracked": (BOX_WIDTH),
    "changed": BOX_WIDTH+10 ,
    "staged": BOX_WIDTH+20,
    "committed": BOX_WIDTH+30,
}

# Colors (curses color pairs)
STATUS_COLORS = {
    "magenta": 1,   # magenta
    "red": 2,     # red
    "green": 3,      # green
    "yellow": 4,   # yellow
    "cyan": 5
}
