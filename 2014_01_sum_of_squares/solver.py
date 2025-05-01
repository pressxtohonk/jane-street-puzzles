from ortools.linear_solver import pywraplp


SOLVER_ID = "CP_SAT"  # https://github.com/coin-or/Cbc

N = 5  # grid size
I = range(N)  # row index
J = range(N)  # col index


def sum_of_squares(solver: pywraplp.Solver) -> dict:
    inf = solver.infinity()

    # matrix of decision variables for each cell
    x = [[solver.IntVar(0, 9, name=f"x_{i}_{j}") for j in J] for i in I]

    # vector of row quotients
    q_r = [solver.IntVar(0, inf, name=f"r_{i}") for i in I]

    # vector of col quotients
    q_c = [solver.IntVar(0, inf, name=f"c_{j}") for j in J]

    # row divisibility constraints
    for i, divisor in enumerate([1, 2, 3, 4, 5]):
        dividend = sum(10 ** (N - 1 - j) * x[i][j] for j in J)
        solver.Add(dividend == q_r[i] * divisor)

    # col divisibility constraints
    for j, divisor in enumerate([6, 7, 8, 9, 10]):
        dividend = sum(10 ** (N - 1 - i) * x[i][j] for i in I)
        solver.Add(dividend == q_c[j] * divisor)

    # Maximize sum of decision variables
    solver.Maximize(sum(x[i][j] for i in I for j in J))

    # Return variables for printing solution
    return {"x": x, "q_r": q_r, "q_c": q_c}


def display_solution(x: list[list[pywraplp.Variable]], **_):
    print("Grid values:")
    print("\n".join(" ".join(f"{x[i][j].solution_value():.0f}" for j in J) for i in I))


def display_quotients(q_r: list[pywraplp.Variable], q_c: list[pywraplp.Variable], **_):
    print("Row quotients:")
    for i in I:
        print(i, q_r[i].solution_value())
    print("Col quotients:")
    for j in J:
        print(j, q_c[j].solution_value())


if __name__ == "__main__":
    # Get an SCIP solver instance for MLIP
    solver: pywraplp.Solver
    if not (solver := pywraplp.Solver.CreateSolver(SOLVER_ID)):
        raise RuntimeError(f"could not instantiate {SOLVER_ID} solver")

    # Instantiate problem variables, constraints and objective
    variables = sum_of_squares(solver)
    x = variables["x"]
    q_r = variables["q_r"]
    q_c = variables["q_c"]

    # Solve!
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print("Objective value =", solver.Objective().Value())
        display_solution(**variables)
        display_quotients(**variables)
    else:
        print("No optimal solution")
