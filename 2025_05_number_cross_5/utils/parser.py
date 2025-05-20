#!/usr/bin/env python

from dataclasses import dataclass
from string import digits

type Grid = list[list[int | None]]


@dataclass
class Puzzle:
    regions: Grid
    highlights: Grid

    @property
    def nrow(self):
        return len(self.regions)

    @property
    def ncol(self):
        return len(self.regions[0])


def parse_puzzle(text: str) -> Puzzle:
    regions_text, highlights_text = text.split("\n\n")
    regions = parse_grid(regions_text)
    highlights = parse_grid(highlights_text)
    return Puzzle(regions, highlights)


def parse_grid(text: str) -> Grid:
    return [
        [int(x) if x in digits else None for x in row.split()]
        for row in text.split("\n")
    ]


def test_parse_puzzle():
    expected_regions = [
        [0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [2, 1, 1, 0, 0],
        [2, 2, 1, 1, 0],
    ]

    expected_highlights = [
        [0, 0, None, None, None],
        [0, None, None, None, None],
        [None, None, None, None, None],
        [None, None, None, None, 0],
        [None, None, None, 0, 0],
    ]

    puzzle = parse_puzzle(
        "0 0 0 0 0\n"
        "1 0 0 0 0\n"
        "1 1 0 0 0\n"
        "2 1 1 0 0\n"
        "2 2 1 1 0\n"
        "\n"
        "0 0 . . .\n"
        "0 . . . .\n"
        ". . . . .\n"
        ". . . . 0\n"
        ". . . 0 0\n"
    )

    assert all(
        puzzle.regions[i][j] == expected_regions[i][j]
        for i in range(5)
        for j in range(5)
    )

    assert all(
        puzzle.highlights[i][j] == expected_highlights[i][j]
        for i in range(5)
        for j in range(5)
    )


if __name__ == "__main__":
    print(parse_puzzle(open(0).read()))
