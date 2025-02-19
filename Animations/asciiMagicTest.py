import asciimagic
import time

# Create an animation from a list of ASCII art frames
frames = [
    '''
     o
    /|\\
    / \\
    ''',
    '''
     o
    /|\\
    / \\
    '''
]

for frame in frames:
    asciimagic.render(frame)
    time.sleep(1)
