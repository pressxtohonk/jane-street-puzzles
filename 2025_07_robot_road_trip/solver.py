from sympy import *


"""
Begin the solve by loosely formalizing the problem as a function over discrete values.
We'll move to an algebraic approach once the shape of the problem emerges.
"""


def naive_solve(v_min, v_max, a_min, a_max, N):
    """Naively solve for the value of a that minimizes mean displacement cost"""
    return min(
        range(a_min, a_max),
        key=lambda a: c_bar(a, v_min, v_max, N),
    )


def c_bar(a, v_min, v_max, N):
    """Average displacement cost for a given speed limit a"""
    return sum(
        p_overtake(v_fast, v_slow, N) * c_overtake(v_fast, v_slow, a)
        for v_fast in range(v_min, v_max)
        for v_slow in range(v_min, v_max)
    )


def p_overtake(v_fast, v_slow, N):
    """Probability that a fast car needs to overtake a slow car."""
    return N * ((N / v_slow) - (N / v_fast))


def c_overtake(v_fast, v_slow, a):
    """Displacement cost of a fast car overtaking a slow car."""
    if v_slow <= a <= v_fast:
        return 0
    if v_slow <= v_fast <= a:
        return 2 * c_decelerate(curr=v_slow, target=0)
    if a <= v_slow <= v_fast:
        return 2 * c_decelerate(curr=v_slow, target=a)


def c_decelerate(curr, target):
    """Displacement cost of decelerating from curr to target"""
    return (curr - target) ** 2


"""
1. At this point, note that we can simplify to exploit the multiplicative minimization objective:

    p_overtake(...) * c_overtake(...)

- Constant coefficient N dropped from p_overtake component
- Constant coefficient 2 dropped from c_overtake component


2. Additionally, the domain of c_overtake branches into 3 regions, of which only 2 are non-zero:

- slow lane overtake: v_slow <= v_fast <= a, c_overtake only depends on v_slow
- fast lane overtake: a <= v_slow <= v_fast, c_overtake only depends on v_slow and a


3. Finally, note that c_decelerate is invariant to translation, i.e:

- c_decelerate(a, b) == c_decelerate(a+c, b+c) for all c
"""


def simplified_solve(v_min, v_max):
    """Naive solve, but with simplifications exploiting the multiplicative objective:"""

    return min(
        range(v_min, v_max),  # NOTE: a < v_min is dominated by a = v_min
        key=lambda a: _c_bar(v_min, a, target=0) + _c_bar(a, v_max, target=a),
    )


def _c_bar(v_min, v_max, target):
    """Average displacement cost for a region where the slower car must decelerate to allow an overtake

    Exploits (2) and (3).
    """

    return sum(
        _p_overtake(v_slow, v_fast) * c_decelerate(curr=v_slow, target=target)
        for v_slow in range(v_min, v_max)
        for v_fast in range(v_slow, v_max)
    )


def _p_overtake(v_fast, v_slow):
    """p_overtake with constant coefficients dropped. Suitable for linear minimization objectives"""
    return 1 / v_slow - 1 / v_fast


"""
Note that simplified solve decomposes to c_bar, which corresponds to evaluating an integral.
"""


def get_partial_cost_solver():
    """Generate an integral for a sub-domain of the problem space."""
    x, y, A, B, C = symbols("x y A B C")

    v_min = A
    v_max = B
    target = C
    v_fast = x
    v_slow = y

    expression = _p_overtake(v_slow, v_fast) * c_decelerate(curr=v_slow, target=target)
    domain_v_slow = (v_min, v_max)
    domain_v_fast = (v_slow, v_max)

    print("# Generating integral")
    print(f"{expression = }")
    print(f"domain({v_slow}) = {domain_v_slow}")
    print(f"domain({v_fast}) = {domain_v_fast}")

    print(f"# Integrating wrt {v_fast} and {v_slow}")
    result = integrate(expression, (v_fast, v_slow, v_max), (v_slow, v_min, v_max))
    result = result.simplify()
    print(f"{result = }")

    def solver(v_min, v_max, target):
        return result.subs([(A, v_min), (B, v_max), (C, target)])

    return solver


def get_avg_displacement_cost(a, v_min, v_max):
    """Reconstruct full integral from sub-domain integrals."""
    get_partial_cost = get_partial_cost_solver()
    c_slow_lane = get_partial_cost(v_min, a, target=0)
    c_fast_lane = get_partial_cost(a, v_max, target=a)
    return c_slow_lane + c_fast_lane


def get_stationary_point(v_min, v_max, epsilon):
    """Binary search over a to find a stationary point that maximizes/minimizes the integral"""
    a = symbols("a")

    cost_func = get_avg_displacement_cost(a=a, v_min=v_min, v_max=v_max)
    cost_grad = diff(cost_func, a)

    a_min = v_min
    a_max = v_max

    while a_max - a_min > epsilon:
        a_hat = (a_min + a_max) / 2
        dydx = cost_grad.subs(a, a_hat).simplify()
        if abs(dydx) < epsilon:
            return a_hat
        if dydx < 0:
            a_max = a_hat
        elif dydx > 0:
            a_min = a_hat


"""
Plugging in our initial conditions should give a solution.
"""

if __name__ == "__main__":
    params = dict(
        v_min=1.0,
        v_max=2.0,
        epsilon=1e-12,
    )
    print(f"{params = }")

    a_star = get_stationary_point(**params)
    print(f"{a_star = :.10f}")
