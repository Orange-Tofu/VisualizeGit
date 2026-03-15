# core/ui_config.py

# Terminal Width and Height
MIN_TERMINAL_HEIGHT = 30
MIN_TERMINAL_WIDTH = 110

# Generic UI constants
BOX_HEIGHT = 6
BOX_WIDTH = 14
ROW_Y = 3
BOTTOM_ROW_TEXT_Y = 10

# X positions for git status boxes
STATUS_X_POSITIONS = {
    "untracked": 5,
    "changed": 25,
    "staged": 45,
    "committed": 65,
}

# Colors (rich styles)
STATUS_COLORS = {
    "magenta": "magenta",
    "red": "red",
    "green": "green",
    "yellow": "yellow",
    "cyan": "cyan"
}
