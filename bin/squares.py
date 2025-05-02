#!/usr/bin/env python


def squares_before(n: int):
    for i in range(1, 1 + int(n**0.5)):
        yield i * i


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("upper_bound", type=int)
    args = parser.parse_args()

    for p in squares_before(args.upper_bound):
        print(p)


if __name__ == "__main__":
    main()
