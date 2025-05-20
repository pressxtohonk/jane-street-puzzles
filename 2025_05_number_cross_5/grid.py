from dataclasses import dataclass
from itertools import pairwise, product
from typing import Self
from ortools.sat.python import cp_model

from utils.tiling import Tiling, get_tilings


@dataclass
class Grid:
    model: cp_model.CpModel
    label: list[list[cp_model.IntVar]]
    tiled: list[list[cp_model.IntVar]]
    value: list[list[cp_model.IntVar]]
    bools: list[list[list[cp_model.IntVar]]]
    incoming: list[list[list[cp_model.IntVar]]]
    outgoing: list[list[list[cp_model.IntVar]]]

    # Internals
    _tilings: list[Tiling]
    _pattern: list[list[cp_model.IntVar]]

    @property
    def display_callback(self) -> cp_model.CpSolverSolutionCallback:
        return DisplayCallback(self)

    @classmethod
    def from_regions(
        cls,
        model: cp_model.CpModel,
        grid: list[list[int]],
        highlights: list[list[bool]],
    ) -> Self:
        """Initialize decision variables for a grid and add constraints for basic logic"""
        nrow = len(grid)
        ncol = len(grid[0])

        I = range(nrow)
        J = range(ncol)

        def _adjacencies(grid: list[list[int]]) -> set[tuple[int, int]]:
            """Given a grid of region labels, returns a set of adjacent region pairs"""
            nrow = len(grid)
            ncol = len(grid[0])
            return set(
                (curr, peer) if curr < peer else (peer, curr)
                for i in range(1, nrow)
                for j in range(1, ncol)
                for (di, dj) in [(0, -1), (-1, 0)]
                if (curr := grid[i][j]) != (peer := grid[i + di][j + dj])
            )

        def _peers(i: int, j: int):
            """Returns all adjacent grid coordinates to a given coordinate"""
            return filter(
                lambda ij: ij[0] in I and ij[1] in J,
                [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)],
            )

        def _grid_of(init):
            """Initializes a grid similar in shape to the puzzle grid with an init function"""
            return [[init(i, j) for j in J] for i in I]

        # Auxiliary variables
        _tilings = list(get_tilings(ncol))
        _pattern = [
            [model.NewBoolVar(f"t[{i}]={t}") for t, _ in enumerate(_tilings)] for i in I
        ]

        _regions = set(region for row in grid for region in row)
        _region_label = [model.NewIntVar(1, 9, f"region[{x}]") for x in _regions]

        # Collect grids of underlying decision vars
        label = _grid_of(lambda i, j: _region_label[grid[i][j]])
        tiled = _grid_of(lambda i, j: model.NewBoolVar(f"z[{i},{j}]"))
        value = _grid_of(lambda i, j: model.NewIntVar(0, 9, f"x[{i},{j}]"))
        bools = _grid_of(
            lambda i, j: [model.NewBoolVar(f"x[{i},{j}]={k}") for k in range(10)]
        )

        # Collect lists of all possible inflows and outflows from each cell (each flow is an auxiliary variable)
        incoming = _grid_of(lambda i, j: [])
        outgoing = _grid_of(lambda i, j: [])
        for i, j in product(I, J):
            if not highlights[i][j]:
                for r, c in _peers(i, j):
                    if not highlights[r][c]:
                        aux = model.NewIntVar(0, 9, f"({i},{j}) to ({r},{c})")
                        outgoing[i][j].append(aux)
                        incoming[r][c].append(aux)

        # Cells must be filled with have exactly one digit (0 for tiled cells)
        for i, j in product(I, J):
            total = label[i][j] + sum(incoming[i][j]) - sum(outgoing[i][j])
            model.Add(value[i][j] == total)
            model.AddExactlyOne(bools[i][j])
            [model.Add(total == k).OnlyEnforceIf(bools[i][j][k]) for k in range(10)]

            # Tiled cell constraints
            [
                constraint.OnlyEnforceIf(tiled[i][j])
                for constraint in [
                    model.Add(sum(outgoing[i][j]) == label[i][j]),
                    model.Add(sum(incoming[i][j]) == 0),
                    model.Add(value[i][j] == 0),
                ]
            ]

            # Non-tiled cell constraints
            [
                constraint.OnlyEnforceIf(tiled[i][j].Not())
                for constraint in [
                    model.Add(sum(outgoing[i][j]) == 0),
                    model.Add(value[i][j] != 0),
                ]
            ]

        # Adjacent regions must have different labels
        [model.Add(_region_label[i] != _region_label[j]) for i, j in _adjacencies(grid)]

        # Tiled cells cannot be joined by an edge
        [
            model.AddAtMostOne(tiled[i1][j], tiled[i2][j])
            for j in J
            for i1, i2 in pairwise(I)
        ]

        # Every row must have exactly one assigned tiling pattern
        [model.AddExactlyOne(_pattern[i]) for i in I]

        # All row tilings must follow valid patterns
        [
            model.Add(tiled[i][j] == tiling_t.tiled[j]).OnlyEnforceIf(_pattern[i][t])
            for t, tiling_t in enumerate(_tilings)
            for i, j in product(I, J)
        ]

        return cls(
            model=model,
            label=label,
            tiled=tiled,
            value=value,
            bools=bools,
            incoming=incoming,
            outgoing=outgoing,
            _tilings=_tilings,
            _pattern=_pattern,
        )


class DisplayCallback(cp_model.CpSolverSolutionCallback):
    def __init__(self, grid: Grid):
        super().__init__()
        self.soln = 0
        self.grid = grid

    def _show_cell(self, cell) -> str:
        return str(self.Value(cell))

    def _show_grid(self, grid: list[list]) -> None:
        print(
            "\n".join(" ".join(self._show_cell(cell) for cell in row) for row in grid)
        )

    def OnSolutionCallback(self) -> None:
        self.soln += 1
        print("soln", self.soln)

        print("labels")
        self._show_grid(self.grid.label)

        print("tiled")
        self._show_grid(self.grid.tiled)

        print("value")
        self._show_grid(self.grid.value)
