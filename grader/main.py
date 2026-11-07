"""CodeKita grader API.

POST /grade  {code, exercise_id} -> per-test pass/fail + friendly summary.
Student-facing responses never contain stack traces; errors are logged
server-side only.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from grader.runner import run_code
except ImportError:
    from runner import run_code

log = logging.getLogger("codekita.grader")
logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parent.parent
EX_DIR = ROOT / "content" / "exercises"

app = FastAPI(title="CodeKita Grader")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])


def load_exercise(exercise_id: str) -> dict:
    for f in EX_DIR.glob("*.json"):
        for ex in json.loads(f.read_text())["exercises"]:
            if ex["id"] == exercise_id:
                return ex
    raise HTTPException(404, "Exercise not found")


class GradeRequest(BaseModel):
    code: str = Field(max_length=20_000)
    exercise_id: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/grade")
def grade(req: GradeRequest):
    ex = load_exercise(req.exercise_id)
    results, passed = [], 0
    sandbox = "none"
    for i, tc in enumerate(ex["tests"]):
        r = run_code(req.code, tc.get("stdin", ""))
        sandbox = r.sandbox
        if r.error:
            log.info("exercise=%s test=%s error=%s", req.exercise_id, i, r.error)
        if r.timed_out:
            results.append({"case": i + 1, "passed": False, "feedback": "Program took too long — check for an infinite loop."})
            continue
        ok = r.stdout.strip() == tc["expected_stdout"].strip()
        passed += ok
        results.append({"case": i + 1, "passed": ok,
                        "feedback": "Correct!" if ok else f"Expected output: {tc['expected_stdout'].strip()!r} — check your blocks and try again."})
    all_passed = passed == len(ex["tests"])
    return {"exercise_id": req.exercise_id, "concept": ex["concept"],
            "passed": all_passed, "score": passed / max(1, len(ex["tests"])),
            "results": results, "sandbox": sandbox,
            "summary": "Great work — all checks passed!" if all_passed
                       else f"{passed} of {len(ex['tests'])} checks passed. Keep going!"}
