#!/usr/bin/env python

from ortools.sat.python import cp_model
from puzzle import actual_puzzle, example_puzzle


def solve_example():
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    solver.parameters.log_to_stdout = True
    solver.parameters.log_search_progress = True
    example_puzzle(model, solver)


def solve_actual():
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    solver.parameters.log_to_stdout = True
    solver.parameters.log_search_progress = True
    actual_puzzle(model, solver)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser("Number Cross 5")
    parser.add_argument("-m", "--main", action="store_true")
    parser.add_argument("-t", "--test", action="store_true")
    args = parser.parse_args()

    if not (args.test or args.main):
        print("Nothing will run. Try passing --test or --main to trigger a solve")

    if args.test:
        print("TEST: Solving the example puzzle")
        solve_example()

    if args.main:
        print("MAIN: Solving the actual puzzle")
        solve_actual()


if __name__ == "__main__":
    main()
