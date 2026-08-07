"""
Bayesian Knowledge Tracing (BKT) update logic.

Stateless/pure -- takes numbers in, returns numbers out, no DB dependency.
Makes it directly testable and reusable inside agents later.
"""


def update_p_know(
    p_know: float,
    correct: bool,
    p_slip: float,
    p_transit: float,
    p_guess: float,
) -> float:
    """
    Runs one BKT update step given a single observed attempt.
    """
    if correct:
        numerator = p_know * (1 - p_slip)
        denominator = p_know * (1 - p_slip) + (1 - p_know) * p_guess
    else:
        numerator = p_know * p_slip
        denominator = p_know * p_slip + (1 - p_know) * (1 - p_guess)

    if denominator == 0:
        p_know_given_obs = p_know
    else:
        p_know_given_obs = numerator / denominator

    p_know_next = p_know_given_obs + (1 - p_know_given_obs) * p_transit

    return max(0.0, min(1.0, p_know_next))


MASTERY_THRESHOLD = 0.6