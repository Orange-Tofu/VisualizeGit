from tqdm import tqdm
import time

for i in tqdm(range(10), desc="Loading...", ncols=100, colour="green"):
    time.sleep(0.5)
