from ortools.sat.python import cp_model


N = 9  # grid size
I = range(N)  # row index
J = range(N)  # col index

regions = [
    [int(x) for x in row.split()]
    for row in [
        "0 0 0 1 1 1 2 2 2",
        "0 0 0 1 1 1 2 2 2",
        "0 0 0 1 1 1 2 2 2",
        "3 3 3 4 4 4 5 5 5",
        "3 3 3 4 4 4 5 5 5",
        "3 3 3 4 4 4 5 5 5",
        "6 6 6 7 7 7 8 8 8",
        "6 6 6 7 7 7 8 8 8",
        "6 6 6 7 7 7 8 8 8",
    ]
]

boxes = [[(i, j) for i in I for j in J if regions[i][j] == box] for box in range(9)]


def somewhat_square_sudoku(model: cp_model.CpModel):
    # Decision vars
    x = {(i, j): model.NewIntVar(0, 9, f"x{i}{j}") for i in I for j in J}
    row = [model.NewIntVar(12345678, 987654321, f"r{i}") for i in I]
    gcd = model.NewIntVar(1, 999_999_999, "y")
    exc = model.NewIntVar(0, 9, "z")

    # Sudoku rules
    [model.AddAllDifferent(x[i, j] for i in I) for j in J]
    [model.AddAllDifferent(x[i, j] for j in J) for i in I]
    [model.AddAllDifferent(x[i, j] for i, j in box) for box in boxes]

    # Exclude 1 digit from the grid
    [model.Add(x[i, j] != exc) for i in I for j in J]

    # Given digits
    model.Add(x[0, 7] == 2)
    model.Add(x[1, 8] == 5)
    model.Add(x[2, 1] == 2)
    model.Add(x[3, 2] == 0)
    model.Add(x[5, 3] == 2)
    model.Add(x[6, 4] == 0)
    model.Add(x[7, 5] == 2)
    model.Add(x[8, 6] == 5)

    # GCD constraints
    [model.Add(row[i] == sum(x[i, j] * 10 ** (8 - j) for j in J)) for i in I]
    [model.AddModuloEquality(0, row[i], gcd) for i in I]

    # Hueristics
    # - In any sudoku, columns contain the same digits and must have the same sum.
    # - The grid sum must be a multiple of 111_111_111 (prime factors: 3 * 3 * 37 * 333667).
    # - Since the GCD of rows must divide the grid sum, it comprises factors of the grid sum.
    # - We guess that the optimal soln requires the GCD divide by 333667, the largest factor.
    model.AddModuloEquality(0, gcd, 333667)

    # Maximize GCD
    model.Maximize(gcd)

    return {"x": x, "y": gcd, "z": exc, "r": row}


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.r = variables["r"]
        self.x = variables["x"]
        self.y = variables["y"]
        self.z = variables["z"]
        self.n = 0

    def on_solution_callback(self) -> None:
        self.n += 1
        print("solution", self.n)
        print("row =", self.Value(self.r[4]))
        print("obj =", self.Value(self.y))
        print("exc =", self.Value(self.z))
        print("\n".join(" ".join(str(self.Value(self.x[i, j])) for j in J) for i in I))


if __name__ == "__main__":
    model = cp_model.CpModel()
    variables = somewhat_square_sudoku(model)

    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = False

    print_soln = SolutionPrinter(variables)
    status = solver.Solve(model, solution_callback=print_soln)
    match status:
        case cp_model.OPTIMAL:
            print("OPTIMAL")
        case cp_model.UNKNOWN:
            print("UNKNOWN")
        case cp_model.FEASIBLE:
            print("FEASIBLE")
        case cp_model.INFEASIBLE:
            print("INFEASIBLE")
        case cp_model.MODEL_INVALID:
            print("MODEL_INVALID")
