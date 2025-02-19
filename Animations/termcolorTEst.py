from termcolor import colored
import time

for i in range(10):
    print(colored(f"Frame {i}", 'cyan'))
    time.sleep(0.5)
