from functools import lru_cache


@lru_cache
def fibonacci(limit: int):
    def f(n: int):
        prev = 0
        curr = 1
        while curr < n:
            yield curr
            prev, curr = curr, prev + curr

    return list(f(limit))


@lru_cache
def powerset(n: int):
    def f(n: int):
        if n == 0:
            yield ()
            return
        for ys in powerset(n - 1):
            yield ys
            yield (n - 1, *ys)

    return list(f(n))


@lru_cache
def primes(limit: int):
    def f(n: int):
        factors = {}
        for q in range(2, n):
            if q not in factors:
                factors[q * q] = [q]
                yield q
            else:
                for p in factors[q]:
                    factors.setdefault(p + q, []).append(p)
                del factors[q]

    return list(f(limit))


@lru_cache
def squares(limit: int):
    def f(n: int):
        ub = int(n**0.5)
        for i in range(1, ub + 1):
            yield i * i

    return list(f(limit))
