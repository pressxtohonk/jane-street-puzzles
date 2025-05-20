from typing import Callable, Iterable, Sequence
from ortools.sat.python import cp_model

from grid import Grid
from utils.series import fibonacci, primes, squares


# Puzzle definitions
def example_puzzle(model: cp_model.CpModel, solver: cp_model.CpSolver):
    """Model the example problem to understand how tractable this problem is"""

    grid = Grid.from_regions(
        model=model,
        grid=[
            [int(x) for x in row.split()]
            for row in [
                "0 0 0 0 0",
                "1 0 0 0 0",
                "1 1 0 0 0",
                "2 1 1 0 0",
                "2 2 1 1 0",
            ]
        ],
        highlights=[
            [x != "." for x in row.split()]
            for row in [
                "x x . . .",
                "x . . . .",
                ". . . . .",
                ". . . . x",
                ". . . x x",
            ]
        ],
    )

    add_row_constraint(grid, 0, ensure_divisible_by(model, 11))
    add_row_constraint(grid, 1, ensure_divisible_by(model, 14))
    add_row_constraint(grid, 2, ensure_divisible_by(model, 28))
    add_row_constraint(grid, 3, ensure_divisible_by(model, 101))
    add_row_constraint(grid, 4, ensure_divisible_by(model, 2025))

    status = solver.Solve(model, solution_callback=grid.display_callback)
    print(solver.StatusName(status))


def actual_puzzle(model: cp_model.CpModel, solver: cp_model.CpSolver):
    grid = Grid.from_regions(
        model=model,
        grid=[
            [int(x) for x in row.split()]
            for row in [
                "0 0 0 0 0 0 0 0 0 0 0",
                "0 1 0 0 0 0 0 0 0 0 0",
                "1 1 2 2 2 2 3 3 3 0 3",
                "1 2 2 1 2 4 3 3 3 3 3",
                "1 2 2 1 2 4 4 3 3 4 3",
                "1 1 1 1 1 4 4 4 4 4 3",
                "1 5 6 6 1 1 4 4 6 4 4",
                "1 5 6 6 6 6 6 6 6 7 7",
                "5 5 5 5 6 5 6 7 7 7 7",
                "5 5 5 5 5 5 5 5 5 5 5",
                "5 5 8 8 8 8 8 8 5 5 5",
            ]
        ],
        highlights=[
            [x != "." for x in row.split()]
            for row in [
                ". . . . . . . . . . .",
                ". . . x x . . . . . .",
                ". . . . x . . . . x .",
                ". . . . . . . . x x .",
                ". . . . . . . . . . .",
                ". . . . . x . . . . .",
                ". x x . . x x . . . .",
                ". x . . . x . . . . .",
                ". . . . x x . . . . .",
                ". . . . x . . . . . .",
                ". . . . . . . . . . .",
            ]
        ],
    )

    # Prophylactic solution for row 11 inferred after exploring solver solution for first 10 rows 🙂 ↕️
    hint = [
        [int(x) if x != "." else None for x in row.split()]
        for row in [
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            ". . . . . . . . . . .",
            "0 4 7 0 8 8 7 0 4 3 3",
        ]
    ]

    assert all(
        int(n) in primes(1000) for n in "".join(map(str, hint[10])).split("0") if n
    )

    for i, row in enumerate(hint):
        for j, k in enumerate(row):
            if k is not None:
                model.AddHint(grid.value[i][j], k)
                model.AddHint(grid.bools[i][j][k], True)

    print("Adding constraints")
    add_row_constraint(grid, 0, ensure_square(model))
    add_row_constraint(grid, 1, ensure_product_is(model, 20))
    add_row_constraint(grid, 2, ensure_divisible_by(model, 13))
    add_row_constraint(grid, 3, ensure_divisible_by(model, 32))
    add_row_constraint(grid, 4, ensure_self_dividing(model))
    add_row_constraint(grid, 5, ensure_product_is(model, 25))
    add_row_constraint(grid, 6, ensure_self_dividing(model))
    add_row_constraint(grid, 7, ensure_odd_palindrome(model))
    add_row_constraint(grid, 8, ensure_fibonacci(model))
    add_row_constraint(grid, 9, ensure_product_is(model, 2025))
    add_row_constraint(grid, 10, ensure_remainder(model, 2, 1))
    add_non_repeating_numbers_constraint(grid, model)

    print("Solving")
    status = solver.Solve(model, solution_callback=grid.display_callback)
    print(solver.StatusName(status))


# Variable manipulation helpers
def as_digits(number: int) -> list[int]:
    digits = []
    while number:
        number, d = divmod(number, 10)
        digits.append(d)
    return digits[::-1]


# Constraints
def add_row_constraint(
    grid: Grid,
    i: int,
    get_constraints: Callable[
        [Sequence[cp_model.IntVar], Sequence[list[cp_model.IntVar]]],
        Iterable[cp_model.Constraint],
    ],
):
    """Adds optional constraints to all un-tiled numbers in a row"""
    [
        constraint.OnlyEnforceIf(grid._pattern[i][t])
        for t, tiling_t in enumerate(grid._tilings)
        for group in tiling_t.groups
        for constraint in get_constraints(
            [grid.value[i][j] for j in group.cells],
            [grid.bools[i][j] for j in group.cells],
        )
    ]


def add_non_repeating_numbers_constraint(grid: Grid, model: cp_model.CpModel):
    """Adds constraints to ensure un-tiled numbers do not repeat in the grid"""

    def as_number(digits: list[cp_model.IntVar]):
        n = len(digits)
        return sum(d * 10 ** (n - i - 1) for i, d in enumerate(digits))

    # Enforce uniqueness within rows
    [
        constraint.OnlyEnforceIf(grid._pattern[i][t])
        for i, row in enumerate(grid.value)
        for t, tiling_t in enumerate(grid._tilings)
        for a, g1 in enumerate(tiling_t.groups)
        for b, g2 in enumerate(tiling_t.groups)
        if a < b
        for constraint in [
            model.Add(
                as_number([row[j] for j in g1.cells])
                != as_number([row[j] for j in g2.cells])
            )
        ]
    ]

    # Enforce uniqueness between rows
    [
        constraint.OnlyEnforceIf(grid._pattern[i1][t1], grid._pattern[i2][t2])
        for i1, row1 in enumerate(grid.value)
        for i2, row2 in enumerate(grid.value)
        if i1 < i2
        for t1, tiling_t1 in enumerate(grid._tilings)
        for g1 in tiling_t1.groups
        for t2, tiling_t2 in enumerate(grid._tilings)
        for g2 in tiling_t2.groups
        for constraint in [
            model.Add(
                as_number([row1[j] for j in g1.cells])
                != as_number([row2[j] for j in g2.cells])
            )
        ]
    ]


def ensure_is_one_of(model: cp_model.CpModel, candidates: Sequence[list[int]]):
    def get_constraints(
        digits: Sequence[cp_model.IntVar],
        bools: Sequence[list[cp_model.IntVar]],
    ) -> Iterable[cp_model.Constraint]:
        auxs = []
        for target in filter(lambda x: len(x) == len(digits), candidates):
            aux = model.NewBoolVar("")
            for b, x in zip(bools, target):
                model.Add(b[x] == True).OnlyEnforceIf(aux)
            auxs.append(aux)

        yield model.AddBoolOr(auxs)

    return get_constraints


def ensure_is_in_series(model: cp_model.CpModel, series: Callable[[int], list[int]]):
    def get_constraints(
        digits: Sequence[cp_model.IntVar],
        bools: Sequence[list[cp_model.IntVar]],
    ) -> Iterable[cp_model.Constraint]:
        targets = [as_digits(x) for x in series(10 ** len(digits))]
        yield from ensure_is_one_of(model, targets)(digits, bools)

    return get_constraints


def ensure_square(model: cp_model.CpModel):
    return ensure_is_in_series(model, squares)


def ensure_fibonacci(model: cp_model.CpModel):
    return ensure_is_in_series(model, fibonacci)


def ensure_prime(model: cp_model.CpModel):
    return ensure_is_in_series(model, primes)


def ensure_product_is(model: cp_model.CpModel, target: int):
    def assignments(n: int, target: int) -> list[list[int]]:
        if n == 0:
            return [[]] if target == 1 else []
        result = []
        for d in range(1, 10):
            if target % d == 0:
                for rest in assignments(n - 1, target // d):
                    result.append([d] + rest)
        return result

    def get_constraints(
        digits: Sequence[cp_model.IntVar],
        bools: Sequence[list[cp_model.IntVar]],
    ) -> Iterable[cp_model.Constraint]:
        candidates = assignments(len(digits), target)
        yield from ensure_is_one_of(model, candidates)(digits, bools)

    return get_constraints


def ensure_remainder(model: cp_model.CpModel, divisor: int, remainder: int):
    def get_constraints(
        digits: Sequence[cp_model.IntVar],
        bools: Sequence[list[cp_model.IntVar]],
    ) -> Iterable[cp_model.Constraint]:
        n = len(digits)
        x = sum(d_i * 10 ** (n - i - 1) for i, d_i in enumerate(digits))
        quotient = model.NewIntVar(1, 10**n - 1, "")
        yield model.Add(x == divisor * quotient + remainder)

    return get_constraints


def ensure_divisible_by(model: cp_model.CpModel, divisor: int):
    return ensure_remainder(model, divisor, 0)


def ensure_odd(model: cp_model.CpModel):
    return ensure_remainder(model, 2, 1)


def ensure_self_dividing(model: cp_model.CpModel):
    def get_constraints(
        digits: Sequence[cp_model.IntVar],
        bools: Sequence[list[cp_model.IntVar]],
    ) -> Iterable[cp_model.Constraint]:
        for divisor in range(2, 10):
            aux = model.NewBoolVar("")
            model.Add(sum(b[divisor] for b in bools) <= aux * len(bools))
            for constraint in ensure_divisible_by(model, divisor)(digits, bools):
                yield constraint.OnlyEnforceIf(aux)

    return get_constraints


def ensure_odd_palindrome(model: cp_model.CpModel):
    def get_constraints(
        digits: Sequence[cp_model.IntVar],
        bools: Sequence[list[cp_model.IntVar]],
    ) -> Iterable[cp_model.Constraint]:
        n = len(digits)
        for i in range(n // 2):
            yield model.Add(digits[i] == digits[n - i - 1])
        yield from ensure_odd(model)(digits, bools)

    return get_constraints


if __name__ == "__main__":
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    solver.parameters.log_to_stdout = True
    solver.parameters.log_search_progress = True
    example_puzzle(model, solver)
