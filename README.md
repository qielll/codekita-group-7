# CodeKita — Adaptive Blockly-to-Python Learning Platform (MVP)

A student drags visual blocks → the blocks become Python → the code is
auto-graded in a sandbox → mastery per concept updates → the next,
slightly harder/easier exercise is recommended. Scope contract: see
`MVP_SPEC.md`. Architecture and the adaptive rule: see `ARCHITECTURE.md`.

## Prerequisites
- **Docker** (required for the grader sandbox — there is no non-Docker
  fallback for demos)
- Python 3.12+, Node 20+

## Run it
```bash
# 1) Sandbox image
docker build -t codekita-sandbox:latest -f grader/sandbox.Dockerfile grader/

# 2) Grader API (terminal 1)
pip install -r grader/requirements.txt
uvicorn grader.main:app --port 8000        # from the repo root

# 3) Web app (terminal 2)
cd web && npm install && npm run dev       # http://localhost:5173
```

## Tests
```bash
pip install fastapi uvicorn pydantic httpx pytest
python -m pytest tests/ -q
# On a machine without Docker, tests use the dev-only local sandbox:
CODEKITA_ALLOW_LOCAL_SANDBOX=1 python -m pytest tests/ -q
```

## Add a lesson
1. Add `content/lessons/<id>.json` (explanation, worked example, exercise ids).
2. Add/extend `content/exercises/<concept>.json` with prompts and hidden
   test cases (`expected_stdout` per case). No code changes needed.

## Demo script (5 minutes)
1. Open the web app, enter a name/class code (no password).
2. Lesson 1 → build *First / Second* with two print blocks → watch the
   Python preview appear → **Run & Grade** → friendly pass feedback.
3. Submit a wrong solution → friendly fail, no stack trace.
4. (Grader terminal / API) submit `while True: pass` → it is killed at the
   2 s limit and reported as a timeout; the server stays up.
5. Fail the loops exercise twice → the Progress panel shows loops mastery
   dropping and loops stays the ⭐ recommended concept; pass twice →
   difficulty steps up and the path advances.
