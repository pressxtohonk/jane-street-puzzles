from typing import Callable

def eq(x: float, y: float, epsilon: float = 1e-12) -> bool:
    """relaxed equality check since we only need 10 d.p."""
    return abs(x - y) < epsilon

def at_least_one(p: float, n: int = 2) -> float:
    """probability that at least 1/n trials succeeds"""
    return 1 - (1 - p)**n

def estimate(p: float) -> float:
    """solve a DP for P(exists path sum <= 1)"""
    p0 = p      # Pr(label = 0)
    p1 = 1 - p  # Pr(label = 1)
    s0 = 0.5    # Pr(exists path sum <= 0)
    s1 = 0.5    # Pr(exists path sum <= 1)
    s0_prev = 0
    s1_prev = 0
    while not eq(s1, s1_prev):
        s0_prev = s0
        s1_prev = s1
        s0 = p0 * at_least_one(s0_prev)
        s1 = p0 * at_least_one(s1_prev) + p1 * at_least_one(s0_prev)
    return s1

def solve(
    f: Callable[[float], float],
    x_min: float,
    x_max: float,
    y: float,
) -> float | None:
    while x_min <= x_max:
        x = (x_min + x_max) / 2
        if eq(y, y_hat := f(x)):
            return x
        if y_hat < y:
            x_min = x
        else:
            x_max = x

if __name__ == "__main__":
    soln = solve(
        estimate,  # p => Pr(exists path sum <= 1)
        x_min=0.5, # p_min
        x_max=1,   # p_max
        y=0.5,     # Pr(exists path sum <= 1) = 0.5
    )
    print(f"{soln:.10f}")
