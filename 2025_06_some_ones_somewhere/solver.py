from dataclasses import dataclass
from itertools import pairwise
from typing import Callable, Protocol
from ortools.sat.python.cp_model import (
    OPTIMAL,
    CpSolver,
    CpModel,
    CpSolverSolutionCallback,
    IntVar,
    IntervalVar,
)


import puzzle


@dataclass
class TileModel:
    """Holds decision variables used to model a tile"""

    x_interval: IntervalVar
    y_interval: IntervalVar
    x: IntVar | None = None
    y: IntVar | None = None


type SolutionHandler = Callable[[puzzle.Grid[puzzle.Tile]], None]


class SolutionCallback(CpSolverSolutionCallback):
    def __init__(self, model: puzzle.Grid[TileModel], handler: SolutionHandler):
        super().__init__()
        self.model: puzzle.Grid[TileModel] = model
        self.handler: SolutionHandler = handler

    def OnSolutionCallback(self) -> None:
        def get_tile_soln(tile: TileModel | None, size: int) -> puzzle.Tile:
            assert tile is not None
            x = self.Value(tile.x_interval.StartExpr())
            y = self.Value(tile.y_interval.StartExpr())
            return puzzle.Tile(x=x, y=y, size=size)

        soln = self.model.map(get_tile_soln)
        self.handler(soln)


def solve(grid: puzzle.Grid[puzzle.Tile]) -> list[puzzle.Grid[puzzle.Tile]]:
    model = CpModel()

    def get_tile_model(tile: puzzle.Tile | None, size: int) -> TileModel:
        if tile is None:
            x = model.NewIntVar(0, 44, "")
            y = model.NewIntVar(0, 44, "")
            model.Add(x + size <= 45)
            model.Add(y + size <= 45)
            return TileModel(
                x_interval=model.NewIntervalVar(x, size, x + size, ""),
                y_interval=model.NewIntervalVar(y, size, y + size, ""),
                x=x,
                y=y,
            )
        else:
            x = tile.x
            y = tile.y
            model.Add(x + size <= 45)
            model.Add(y + size <= 45)
            return TileModel(
                x_interval=model.NewIntervalVar(x, size, x + size, ""),
                y_interval=model.NewIntervalVar(y, size, y + size, ""),
            )

    grid_model = grid.map(get_tile_model)

    # No overlap constraints
    def get_x_interval(tile: TileModel | None, _: int) -> IntervalVar:
        assert tile is not None
        return tile.x_interval

    def get_y_interval(tile: TileModel | None, _: int) -> IntervalVar:
        assert tile is not None
        return tile.y_interval

    x_intervals = grid_model.map(get_x_interval).squares
    y_intervals = grid_model.map(get_y_interval).squares
    model.AddNoOverlap2D([x for x in x_intervals if x], [y for y in y_intervals if y])

    # Uniqueness constraints
    def enforce_uniqueness(tiles: list[TileModel | None]):
        non_nulls = [
            tile for tile in tiles if tile and tile.x is not None and tile.y is not None
        ]
        for fst, snd in pairwise(non_nulls):
            assert fst.x is not None
            assert fst.y is not None
            assert snd.x is not None
            assert snd.y is not None
            model.Add(45 * fst.y + fst.x < 45 * snd.y + snd.x)

    enforce_uniqueness(grid_model.s1)
    enforce_uniqueness(grid_model.s2)
    enforce_uniqueness(grid_model.s3)
    enforce_uniqueness(grid_model.s4)
    enforce_uniqueness(grid_model.s5)
    enforce_uniqueness(grid_model.s6)
    enforce_uniqueness(grid_model.s7)
    enforce_uniqueness(grid_model.s8)
    enforce_uniqueness(grid_model.s9)

    solver = CpSolver()
    solver.parameters.enumerate_all_solutions = True

    solutions: list[puzzle.Grid[puzzle.Tile]] = []
    solution_callback = SolutionCallback(grid_model, handler=solutions.append)
    status = solver.Solve(model, solution_callback=solution_callback)

    return solutions if status == OPTIMAL else []


if __name__ == "__main__":
    from argparse import ArgumentParser
    import json

    parser = ArgumentParser()
    parser.add_argument("-p", "--path")
    args = parser.parse_args()

    grid = puzzle.parse_grid(args.path)
    match solve(grid):
        case []:
            print("NO SOLUTIONS FOUND")
        case [soln]:
            print(json.dumps([tile.model_dump() for tile in soln.squares]))
        case solns:
            print(len(solns), "SOLUTIONS FOUND")
