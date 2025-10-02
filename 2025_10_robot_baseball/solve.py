from collections.abc import Callable, Sequence
from dataclasses import dataclass


EPSILON = 1e-12

type Vec[T] = Sequence[T]
type Mat[T] = Vec[Vec[T]]


def pitch_matrix(
    p_homerun: float, v_ball: float, v_strike: float, v_homerun: float
) -> Mat[float]:
    """Generates a matrix of values according to pitching rules"""
    payout_ball_wait = v_ball
    payout_strike_wait = v_strike
    payout_ball_swing = v_strike
    payout_strike_swing = p_homerun * v_homerun + (1 - p_homerun) * v_strike

    return [
        [payout_ball_wait, payout_ball_swing],
        [payout_strike_wait, payout_strike_swing],
    ]


def row_policy(m: Mat[float]) -> Vec[float]:
    """Solves for the optimal policy for the row player"""
    ((a, b), (c, d)) = m
    p = (d - c) / (a - b - c + d)
    return (p, 1 - p)


def col_policy(m: Mat[float]) -> Vec[float]:
    """Solves for the optimal policy for the col player"""
    ((a, b), (c, d)) = m
    p = (d - b) / (a - b - c + d)
    return (p, 1 - p)


def game_value(m: Mat[float], pi_row: Vec[float], pi_col: Vec[float]) -> float:
    """Evaluates the game value under the given player policies"""
    return sum(pi_row[i] * pi_col[j] * m[i][j] for i in range(2) for j in range(2))


@dataclass
class Solution:
    expected_score: Mat[float]
    pr_full_count: Mat[float]


def solve(p: float) -> Solution:
    BALLS = [0, 1, 2, 3]
    STRIKES = [0, 1, 2]

    # Set up DP tables
    v = [[0.0 for _ in STRIKES] for _ in BALLS]  # E[Score]
    q = [[0.0 for _ in STRIKES] for _ in BALLS]  # Pr(FullCount | Balls, Strikes)

    # Populate DP tables for each possible pitch
    for ball in reversed(BALLS):
        for strike in reversed(STRIKES):
            # Score matrix for this pitch
            payout_matrix = pitch_matrix(
                p_homerun=p,
                v_ball=1 if ball == 3 else v[ball + 1][strike],
                v_strike=0 if strike == 2 else v[ball][strike + 1],
                v_homerun=4,
            )

            # Pr(Full count) matrix for this pitch
            full_count_probs = pitch_matrix(
                p_homerun=p,
                v_ball=0 if ball == 3 else q[ball + 1][strike],
                v_strike=0 if strike == 2 else q[ball][strike + 1],
                v_homerun=0,
            )

            # Optimal strategies
            pi_pitcher = row_policy(payout_matrix)
            pi_batter = col_policy(payout_matrix)

            # Update DP
            v[ball][strike] = game_value(payout_matrix, pi_pitcher, pi_batter)
            q[ball][strike] = game_value(full_count_probs, pi_pitcher, pi_batter)

            # Enforce initial condition(s)
            if (ball, strike) == (BALLS[-1], STRIKES[-1]):
                q[ball][strike] = 1.0

    return Solution(expected_score=v, pr_full_count=q)


def ternary_search(
    f: Callable[[float], float], lb: float, ub: float, epsilon: float = EPSILON
) -> float:
    """Obtains a near optimal global maxima to a function within the given bounds"""
    while ub - lb > epsilon:
        m1 = lb + (ub - lb) / 3
        m2 = ub - (ub - lb) / 3

        if f(m1) < f(m2):
            lb = m1
        else:
            ub = m2

    return (lb + ub) / 2


def linear_search(
    f: Callable[[float], float], guess: float, epsilon: float = EPSILON
) -> float:
    """Obtains a local maximum to a function around a given point"""
    small = (guess - n * epsilon for n in range(1, 10))
    large = (guess + n * epsilon for n in range(1, 10))
    return max([*small, guess, *large], key=f)


def main():
    def q(p: float) -> float:
        return solve(p).pr_full_count[0][0]

    # ternary search
    print("Pass 1: Ternary search (global)")
    p_star = ternary_search(q, lb=0.0, ub=1.0)
    q_star = q(p_star)
    print(f"q({p_star}) = {q_star}\n")

    # linear search
    print("Pass 2: Linear search (local)")
    p_star = linear_search(q, guess=p_star)
    q_star = q(p_star)
    print(f"q({p_star}) = {q_star}\n")

    # Assert local optima
    assert q_star > q(p_star - EPSILON), f"expected {q_star} >= {q(p_star - EPSILON)}"
    assert q_star > q(p_star + EPSILON), f"expected {q_star} >= {q(p_star + EPSILON)}"

    # Final solution format
    print("Formatted solution")
    print(f"q* = {q_star:.10f} (10 d.p.)")


if __name__ == "__main__":
    main()
