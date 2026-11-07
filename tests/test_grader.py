import os, sys
os.environ["CODEKITA_ALLOW_LOCAL_SANDBOX"] = "1"  # dev-only fallback; Docker absent in this VM
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "grader"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fastapi.testclient import TestClient
from grader.main import app

client = TestClient(app)

def test_correct_solution_passes():
    r = client.post("/grade", json={"code": "print('First')\nprint('Second')", "exercise_id": "seq-1"})
    assert r.status_code == 200 and r.json()["passed"] is True

def test_wrong_solution_fails_friendly():
    r = client.post("/grade", json={"code": "print('Nope')", "exercise_id": "seq-1"})
    body = r.json()
    assert body["passed"] is False
    assert "Traceback" not in str(body)

def test_infinite_loop_times_out_and_server_stays_alive():
    r = client.post("/grade", json={"code": "while True:\n    pass", "exercise_id": "seq-1"})
    assert r.status_code == 200
    assert any("too long" in x["feedback"] for x in r.json()["results"])
    assert client.get("/health").json()["ok"] is True

def test_worked_examples_match_expected():
    import json, glob
    from runner import run_code
    files = glob.glob("content/lessons/*.json")
    assert len(files) == 4
    for f in files:
        lesson = json.load(open(f))
        ex = lesson["example"]
        r = run_code(ex["code"])
        assert not r.timed_out and r.stdout.strip() == ex["expected_stdout"].strip(), (f, r)
