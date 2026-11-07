"""Adaptive recommendation — simple Bayesian Knowledge Tracing (BKT).

Documented rule (see ARCHITECTURE.md):
- Each concept starts at mastery P(L0) = 0.10.
- On an observed answer we first apply the BKT evidence update with
  guess P(G)=0.20 and slip P(S)=0.10, then the learning transition
  P(T)=0.15:
      correct:   P(L|ok)  = P(L)*(1-P(S)) / (P(L)*(1-P(S)) + (1-P(L))*P(G))
      incorrect: P(L|bad) = P(L)*P(S)     / (P(L)*P(S)     + (1-P(L))*(1-P(G)))
      then:      P(L') = P(L|obs) + (1 - P(L|obs)) * P(T)
- Recommendation: the lowest-mastery concept whose prerequisites are all
  >= 0.60 mastery. Difficulty for that concept steps up after 2 consecutive
  successes and down after 2 consecutive failures (clamped 1..3).
"""
from __future__ import annotations

P_INIT, P_GUESS, P_SLIP, P_LEARN = 0.10, 0.20, 0.10, 0.15
PREREQ_THRESHOLD = 0.60

# concept -> prerequisites (order = lesson path)
PREREQS: dict[str, list[str]] = {
    "sequences": [],
    "loops": ["sequences"],
    "conditionals": ["loops"],
    "variables": ["conditionals"],
}


def update_mastery(mastery: float, correct: bool) -> float:
    p = min(max(mastery, 0.0), 1.0)
    if correct:
        num = p * (1 - P_SLIP)
        post = num / (num + (1 - p) * P_GUESS)
    else:
        num = p * P_SLIP
        post = num / (num + (1 - p) * (1 - P_GUESS))
    return round(post + (1 - post) * P_LEARN, 6)


def next_difficulty(current: int, streak_correct: int, streak_wrong: int) -> int:
    if streak_correct >= 2:
        return min(3, current + 1)
    if streak_wrong >= 2:
        return max(1, current - 1)
    return current


def recommend(mastery: dict[str, float]) -> dict:
    """Return {'concept': ..., 'reason': ...} — lowest mastery, prereqs met."""
    for concept in sorted(PREREQS, key=lambda c: mastery.get(c, P_INIT)):
        prereqs = PREREQS[concept]
        if all(mastery.get(p, P_INIT) >= PREREQ_THRESHOLD for p in prereqs):
            if mastery.get(concept, P_INIT) < 0.95:
                return {"concept": concept,
                        "reason": f"Lowest mastery ({mastery.get(concept, P_INIT):.2f}) "
                                  f"with prerequisites met."}
    return {"concept": "variables", "reason": "All concepts mastered — review the hardest concept."}
