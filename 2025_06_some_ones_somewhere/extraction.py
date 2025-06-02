import json
from string import ascii_uppercase

def get_xy(r, c):
    path = f"./board-ones/r{r}c{c}.json"
    with open(path) as f:
        ones = json.load(f)
    return (ones["x"], ones["y"])

def decode(r, c, y, x):
    i = (45 * r + y) % 26
    j = (45 * c + x) % 26
    yield ascii_uppercase[i]
    yield ascii_uppercase[j]

def extract_soln():
    rows = [1, 2, 3]
    cols = [1, 2, 3]

    for r in rows:
        for c in cols:
            x, y = get_xy(r, c)
            yield from decode(r-1, c-1, y, x)

if __name__ == "__main__":
    for char in extract_soln():
        print(char)
