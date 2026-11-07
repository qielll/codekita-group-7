import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "grader"))
from recommend import update_mastery, recommend, next_difficulty, P_INIT

def test_mastery_rises_on_correct_and_falls_on_wrong():
    assert update_mastery(0.5, True) > 0.5
    assert update_mastery(0.5, False) < update_mastery(0.5, True)

def test_repeated_failure_repeats_concept():
    m = {"sequences": 0.9, "loops": 0.3, "conditionals": P_INIT, "variables": P_INIT}
    for _ in range(3):
        m["loops"] = update_mastery(m["loops"], False)
    assert recommend(m)["concept"] == "loops"

def test_repeated_success_steps_up():
    m = {"sequences": P_INIT}
    for _ in range(5):
        m["sequences"] = update_mastery(m["sequences"], True)
    assert m["sequences"] > 0.6  # prereq threshold for loops
    assert recommend({**m, "loops": P_INIT, "conditionals": P_INIT, "variables": P_INIT})["concept"] in ("loops", "sequences")
    assert next_difficulty(1, streak_correct=2, streak_wrong=0) == 2
    assert next_difficulty(2, streak_correct=0, streak_wrong=2) == 1

def test_prereqs_gate_recommendation():
    # conditionals has lowest mastery but its prereq (loops) is not met -> must not recommend it first over an eligible concept
    m = {"sequences": 0.9, "loops": 0.2, "conditionals": 0.0, "variables": 0.0}
    assert recommend(m)["concept"] == "loops"
