#!/usr/bin/env python


def self_dividing_before(n: int):
    for i in range(n):
        digits = set(str(i))
        if '0' in digits:
            continue
        if any(i % int(d) != 0 for d in digits):
            continue
        yield i

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("upper_bound", type=int)
    args = parser.parse_args()

    for p in self_dividing_before(args.upper_bound):
        print(p)


if __name__ == "__main__":
    main()
