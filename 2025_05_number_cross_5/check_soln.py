from collections import Counter
from math import prod
from string import digits


def parse_nums(line: str) -> list[int]:
    line = "".join(x for x in line if x in digits)
    return [int(num) for num in line.split("0") if num]


def as_digits(num: int) -> list[int]:
    res = []
    while num:
        num, r = divmod(num, 10)
        res.append(r)
    return res[::-1]


def square(x: int):
    sqrt = int(x**0.5)
    return x == sqrt * sqrt


def product_of_digits_is(target: int):
    return lambda x: prod(as_digits(x)) == target


def multiple_of(target: int):
    return lambda x: x % target == 0


def divisible_by_each_of_its_digits(x: int):
    return all(multiple_of(d)(x) for d in as_digits(x))


def odd_and_a_palindrome(x: int):
    ds = as_digits(x)
    n = len(ds)
    return ds[0] % 2 == 1 and all(ds[i] == ds[n - 1 - i] for i in range(n // 2))


def fibonacci(x: int):
    a, b = 0, 1
    while b < x:
        a, b = b, a + b
    return b == x


def prime(x: int):
    s = str(x)
    n = len(s)
    with open("../resources/primes.txt") as f:
        for line in f:
            p = line.strip()
            if p == s:
                return True
            elif len(p) > n:
                break
    return False


if __name__ == "__main__":
    checks = [
        square,
        product_of_digits_is(20),
        multiple_of(13),
        multiple_of(32),
        divisible_by_each_of_its_digits,
        product_of_digits_is(25),
        divisible_by_each_of_its_digits,
        odd_and_a_palindrome,
        fibonacci,
        product_of_digits_is(2025),
        prime,
    ]

    lines = list(map(parse_nums, open(0).read().split("\n")))

    for check, nums in zip(checks, lines):
        assert all(map(check, nums))

    nums = [x for nums in lines for x in nums]
    assert all(n == 1 for n in Counter(nums).values())

    print(sum(nums))
