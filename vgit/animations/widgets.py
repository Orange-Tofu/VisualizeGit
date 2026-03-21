# animations/widgets.py
from rich.text import Text

def draw_box(content_char="•", title="Local Ref", style="yellow", left_pad=18):
    """
    Return a multi-line Text representing a box (e.g. for ref storage).
    Parameterized to be reusable across animations.
    """
    pad = " " * left_pad
    box = Text()
    # Top border
    box.append(f"{pad}┌────────────┐\n", style=style)
    # Title line
    title_fixed = title.center(10)
    box.append(f"{pad}│ {title_fixed} │\n", style=style)
    # Content line
    box.append(f"{pad}│     {content_char}      │\n", style=style)
    # Bottom border
    box.append(f"{pad}└────────────┘", style=style)
    return box
