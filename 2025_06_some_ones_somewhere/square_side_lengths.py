from itertools import pairwise
from ortools.sat.python.cp_model import CpSolver, CpModel, IntVar


def square_side_lengths(model: CpModel, solver: CpSolver):
    N = 100

    def square(name: str) -> IntVar:
        return model.NewIntVar(1, N, name)

    board = square("board")
    lb = square("l_blue")
    br = square("brown")
    y = square("yellow")
    b = square("blue")
    r = square("red")
    db = square("d_blue")
    o = square("orange")
    g = square("green")

    squares = [g, o, db, r, b, y, br, lb, board]

    for smaller, bigger in pairwise(squares):
        model.Add(smaller < bigger)

    constraints = [
        (br == 2 * db),
        (r + lb == 2 * y),
        (3 * db == lb + o),
        (3 * db + 2 * y + b + br + r == board),
        (5 * lb == board),
        (3 * br + 3 * y == board),
        (3 * lb + 2 * r + br == board),
        (2 * br == lb + y),
        (lb == r + db),
        (lb == b + o),
        (2 * b == y + r),
        (2 * r == y + o),
        (2 * lb + y + 2 * b + 2 * db == board),
        (2 * lb == br + y + o),
        (br == r + o),
        (2 * y + db == br + 2 * r),
        (y == o + db),
        (br + 2 * r == 2 * lb),
        (2 * b == lb + o),
        (4 * br + b + y == board),
        (2 * y == lb + r),
        (2 * br == lb + y),
        (4 * y + 2 * db + lb == board),
        (4 * b + lb + y + r == board),
        (3 * y + 3 * br == board),
        (2 * lb == r + y + b),
        (3 * r == br + y),
        (3 * br + r + y + lb == board),
        (2 * g + lb == y + b),
    ]

    indicators = []
    for expr in constraints:
        aux = model.NewBoolVar(str(expr))
        model.Add(expr).OnlyEnforceIf(aux)
        indicators.append(aux)

    model.Maximize(sum(indicators))

    status = solver.Solve(model)
    print(solver.StatusName(status))

    for x in squares:
        print(f"{x.Name()}\t{solver.Value(x)}")

    print("violated constraints:")
    for i, expr in zip(indicators, constraints):
        if solver.Value(i) == 0:
            print(expr)


if __name__ == "__main__":
    model = CpModel()
    solver = CpSolver()
    square_side_lengths(model, solver)
