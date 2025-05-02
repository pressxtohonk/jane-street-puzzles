#!/usr/bin/env python


def fibonacci_before(n: int):
    prev = 0
    curr = 1
    while curr < n:
        yield curr
        prev, curr = curr, prev + curr


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("upper_bound", type=int)
    args = parser.parse_args()

    for p in fibonacci_before(args.upper_bound):
        print(p)


if __name__ == "__main__":
    main()
