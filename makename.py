import random
import sys

seed = sys.argv[1] if len(sys.argv) > 1 else ''

with open('BENEDICT.txt') as f:
    if seed:
        lines = f.readlines()
        benedict = lines[hash(seed) % len(lines)].strip()
    else:
        benedict = random.choice(f.readlines()).strip()

with open('CUMBERBATCH.txt') as f:
    if seed:
        lines = f.readlines()
        cumberbatch = lines[hash(seed) % len(lines)].strip()
    else:
        cumberbatch = random.choice(f.readlines()).strip()

print benedict, cumberbatch
