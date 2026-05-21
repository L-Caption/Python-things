import math
import random

rngA = random.randint(1, 100)
rngB = random.randint(rngA + 1, rngA + 100)

n = rngA
while n < rngB:
    print(n)
    n = n + 1