#!/usr/bin/env python

from dataclasses import dataclass
from typing import Iterator


@dataclass
class Tiling:
    tiled: list[bool]  # boolean mask indicating tiled indices
    groups: list["Group"]  # list of untiled groups


@dataclass
class Group:
    cells: list[int]  # indices of cells in the group
    edges: list[int]  # indices of elements bordering the group


# NOTE: Vibe-coded at: https://chatgpt.com/c/6828a75c-1368-8012-a34a-9b15f3b0898b
def get_tilings(n: int) -> Iterator[Tiling]:
    for bits in range(1 << n):
        tile_mask = [(bits >> i) & 1 == 1 for i in range(n)]
        tiles = {i for i, v in enumerate(tile_mask) if v}
        if any((i + 1 in tiles or i + 2 in tiles) for i in tiles):
            continue  # tiles too close

        groups = []
        i = 0
        while i < n:
            if tile_mask[i]:
                i += 1
                continue
            j = i
            while j < n and not tile_mask[j]:
                j += 1
            if j - i < 2:
                break  # invalid group
            edges = []
            if i > 0 and tile_mask[i - 1]:
                edges.append(i - 1)
            if j < n and tile_mask[j]:
                edges.append(j)
            groups.append(Group(list(range(i, j)), edges))
            i = j
        else:
            yield Tiling(tile_mask, groups)


def test_get_tilings():
    assert len(list(get_tilings(1))) == 1  # [x]
    assert len(list(get_tilings(2))) == 1  # [..]
    assert len(list(get_tilings(5))) == 5  # [.....], [x....], [....x], [..x..], [x...x]
    assert len(list(get_tilings(11))) == 54


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Generate valid tilings for a given row size")
    parser.add_argument("n", type=int)
    args = parser.parse_args()

    for tiling in get_tilings(args.n):
        print(tiling)
