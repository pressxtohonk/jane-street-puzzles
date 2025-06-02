import json
from typing import Callable
from pydantic import BaseModel, ConfigDict


class Tile(BaseModel):
    size: int
    x: int
    y: int


class Grid[T](BaseModel):
    s11: T | None = None
    s21: T | None = None
    s22: T | None = None
    s31: T | None = None
    s32: T | None = None
    s33: T | None = None
    s41: T | None = None
    s42: T | None = None
    s43: T | None = None
    s44: T | None = None
    s51: T | None = None
    s52: T | None = None
    s53: T | None = None
    s54: T | None = None
    s55: T | None = None
    s61: T | None = None
    s62: T | None = None
    s63: T | None = None
    s64: T | None = None
    s65: T | None = None
    s66: T | None = None
    s71: T | None = None
    s72: T | None = None
    s73: T | None = None
    s74: T | None = None
    s75: T | None = None
    s76: T | None = None
    s77: T | None = None
    s81: T | None = None
    s82: T | None = None
    s83: T | None = None
    s84: T | None = None
    s85: T | None = None
    s86: T | None = None
    s87: T | None = None
    s88: T | None = None
    s91: T | None = None
    s92: T | None = None
    s93: T | None = None
    s94: T | None = None
    s95: T | None = None
    s96: T | None = None
    s97: T | None = None
    s98: T | None = None
    s99: T | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def squares(self) -> list[T | None]:
        return [
            *self.s1,
            *self.s2,
            *self.s3,
            *self.s4,
            *self.s5,
            *self.s6,
            *self.s7,
            *self.s8,
            *self.s9,
        ]

    @property
    def s1(self) -> list[T | None]:
        return [self.s11]

    @property
    def s2(self) -> list[T | None]:
        return [self.s21, self.s22]

    @property
    def s3(self) -> list[T | None]:
        return [self.s31, self.s32, self.s33]

    @property
    def s4(self) -> list[T | None]:
        return [self.s41, self.s42, self.s43, self.s44]

    @property
    def s5(self) -> list[T | None]:
        return [self.s51, self.s52, self.s53, self.s54, self.s55]

    @property
    def s6(self) -> list[T | None]:
        return [self.s61, self.s62, self.s63, self.s64, self.s65, self.s66]

    @property
    def s7(self) -> list[T | None]:
        return [self.s71, self.s72, self.s73, self.s74, self.s75, self.s76, self.s77]

    @property
    def s8(self) -> list[T | None]:
        return [
            self.s81,
            self.s82,
            self.s83,
            self.s84,
            self.s85,
            self.s86,
            self.s87,
            self.s88,
        ]

    @property
    def s9(self) -> list[T | None]:
        return [
            self.s91,
            self.s92,
            self.s93,
            self.s94,
            self.s95,
            self.s96,
            self.s97,
            self.s98,
            self.s99,
        ]

    def map[V](self, func: Callable[[T | None, int], V]) -> "Grid[V]":
        return Grid(
            s11=func(self.s11, 1),
            s21=func(self.s21, 2),
            s22=func(self.s22, 2),
            s31=func(self.s31, 3),
            s32=func(self.s32, 3),
            s33=func(self.s33, 3),
            s41=func(self.s41, 4),
            s42=func(self.s42, 4),
            s43=func(self.s43, 4),
            s44=func(self.s44, 4),
            s51=func(self.s51, 5),
            s52=func(self.s52, 5),
            s53=func(self.s53, 5),
            s54=func(self.s54, 5),
            s55=func(self.s55, 5),
            s61=func(self.s61, 6),
            s62=func(self.s62, 6),
            s63=func(self.s63, 6),
            s64=func(self.s64, 6),
            s65=func(self.s65, 6),
            s66=func(self.s66, 6),
            s71=func(self.s71, 7),
            s72=func(self.s72, 7),
            s73=func(self.s73, 7),
            s74=func(self.s74, 7),
            s75=func(self.s75, 7),
            s76=func(self.s76, 7),
            s77=func(self.s77, 7),
            s81=func(self.s81, 8),
            s82=func(self.s82, 8),
            s83=func(self.s83, 8),
            s84=func(self.s84, 8),
            s85=func(self.s85, 8),
            s86=func(self.s86, 8),
            s87=func(self.s87, 8),
            s88=func(self.s88, 8),
            s91=func(self.s91, 9),
            s92=func(self.s92, 9),
            s93=func(self.s93, 9),
            s94=func(self.s94, 9),
            s95=func(self.s95, 9),
            s96=func(self.s96, 9),
            s97=func(self.s97, 9),
            s98=func(self.s98, 9),
            s99=func(self.s99, 9),
        )


def add_tile(grid: Grid[Tile], tile: Tile) -> None:
    match tile.size:
        case 1:
            add_s1(grid, tile)
        case 2:
            add_s2(grid, tile)
        case 3:
            add_s3(grid, tile)
        case 4:
            add_s4(grid, tile)
        case 5:
            add_s5(grid, tile)
        case 6:
            add_s6(grid, tile)
        case 7:
            add_s7(grid, tile)
        case 8:
            add_s8(grid, tile)
        case 9:
            add_s9(grid, tile)
        case n:
            raise ValueError(f"tile size {n} should be in 1-9")


def add_s1(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s11:
        grid.s11 = tile
    else:
        raise ValueError("Grid should have <1 1x1 tiles placed")


def add_s2(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s21:
        grid.s21 = tile
    elif not grid.s22:
        grid.s22 = tile
    else:
        raise ValueError("Grid should have <2 2x2 tiles placed")


def add_s3(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s31:
        grid.s31 = tile
    elif not grid.s32:
        grid.s33 = tile
    elif not grid.s33:
        grid.s33 = tile
    else:
        raise ValueError("Grid should have <3 3x3 tiles placed")


def add_s4(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s41:
        grid.s41 = tile
    elif not grid.s42:
        grid.s42 = tile
    elif not grid.s43:
        grid.s43 = tile
    elif not grid.s44:
        grid.s44 = tile
    else:
        raise ValueError("Grid should have <4 4x4 tiles placed")


def add_s5(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s51:
        grid.s51 = tile
    elif not grid.s52:
        grid.s52 = tile
    elif not grid.s53:
        grid.s53 = tile
    elif not grid.s54:
        grid.s54 = tile
    elif not grid.s55:
        grid.s55 = tile
    else:
        raise ValueError("Grid should have <5 5x5 tiles placed")


def add_s6(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s61:
        grid.s61 = tile
    elif not grid.s62:
        grid.s62 = tile
    elif not grid.s63:
        grid.s63 = tile
    elif not grid.s64:
        grid.s64 = tile
    elif not grid.s65:
        grid.s65 = tile
    elif not grid.s66:
        grid.s66 = tile
    else:
        raise ValueError("Grid should have <6 6x6 tiles placed")


def add_s7(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s71:
        grid.s71 = tile
    elif not grid.s72:
        grid.s72 = tile
    elif not grid.s73:
        grid.s73 = tile
    elif not grid.s74:
        grid.s74 = tile
    elif not grid.s75:
        grid.s75 = tile
    elif not grid.s76:
        grid.s76 = tile
    elif not grid.s77:
        grid.s77 = tile
    else:
        raise ValueError("Grid should have <7 7x7 tiles placed")


def add_s8(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s81:
        grid.s81 = tile
    elif not grid.s82:
        grid.s82 = tile
    elif not grid.s83:
        grid.s83 = tile
    elif not grid.s84:
        grid.s84 = tile
    elif not grid.s85:
        grid.s85 = tile
    elif not grid.s86:
        grid.s86 = tile
    elif not grid.s87:
        grid.s87 = tile
    elif not grid.s88:
        grid.s88 = tile
    else:
        raise ValueError("Grid should have <8 8x8 tiles placed")


def add_s9(grid: Grid[Tile], tile: Tile) -> None:
    if not grid.s91:
        grid.s91 = tile
    elif not grid.s92:
        grid.s92 = tile
    elif not grid.s93:
        grid.s93 = tile
    elif not grid.s94:
        grid.s94 = tile
    elif not grid.s95:
        grid.s95 = tile
    elif not grid.s96:
        grid.s96 = tile
    elif not grid.s97:
        grid.s97 = tile
    elif not grid.s98:
        grid.s98 = tile
    elif not grid.s99:
        grid.s99 = tile
    else:
        raise ValueError("Grid should have <9 9x9 tiles placed")


def parse_tiles(path: str | int | None = None) -> list[Tile]:
    path = path or 0
    with open(path) as f:
        tiles = json.load(f)
    return [Tile.model_validate(tile) for tile in tiles]


def parse_grid(path: str | int | None = None) -> Grid[Tile]:
    grid = Grid()
    for tile in parse_tiles(path):
        add_tile(grid, tile)
    return grid


def parse_grids() -> list[list[Grid[Tile]]]:
    return [
        [
            parse_grid("./boards/r1c1.json"),
            parse_grid("./boards/r1c2.json"),
            parse_grid("./boards/r1c3.json"),
        ],
        [
            parse_grid("./boards/r2c1.json"),
            parse_grid("./boards/r2c2.json"),
            parse_grid("./boards/r2c3.json"),
        ],
        [
            parse_grid("./boards/r3c1.json"),
            parse_grid("./boards/r3c2.json"),
            parse_grid("./boards/r3c3.json"),
        ],
    ]


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-p", "--path")
    args = parser.parse_args()

    grid = parse_grid(args.path)
    print(grid)
