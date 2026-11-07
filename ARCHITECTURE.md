# CodeKita — Architecture

## Decisions frozen in Milestone 1
- **Frontend:** Vite + React + TypeScript + Blockly (React chosen; spec allowed either).
- **Progress storage:** browser **localStorage**, keyed by a simple local profile
  (name / class code — no passwords, per spec §2). No account system in v1.
- **Grader:** Python 3 + FastAPI. Lessons/exercises are JSON data files under
  `content/` — adding a lesson means adding files, not code.

## Grader sandbox
`POST /grade {code, exercise_id}` loads the exercise's hidden test cases,
runs the code once per case, and compares stdout (trimmed) to the expected
output. Per-student responses contain only friendly feedback — errors and
stack traces are logged server-side only.

Execution (`grader/runner.py`) defaults to a **fresh Docker container per
run**: `--network none`, 0.5 CPU, 128 MB memory, 64 pids, read-only rootfs,
`--user nobody`, 2 s wall-clock limit, output capped at 10,000 chars.
Student code is never executed on the host in this configuration.

A local subprocess fallback exists **only** behind
`CODEKITA_ALLOW_LOCAL_SANDBOX=1` for development/tests on machines without
Docker. It enforces timeout + rlimits but cannot disable networking, so it
must never be used for a public demo. Every grade response reports which
sandbox ran (`docker` / `local-dev` / `none`).

## Adaptive rule (plain language)
We use simple Bayesian Knowledge Tracing, one mastery score per concept
(sequences → loops → conditionals → variables):

- Every concept starts at **0.10** mastery.
- When a student answers, we update the score with guess = 0.20 and
  slip = 0.10 (a correct answer might be a guess; a wrong one might be a
  slip), then add learning = 0.15 for the practice itself. Correct answers
  push mastery up, wrong answers push it down, and it never jumps straight
  to 0 or 1 in one step.
- **Next exercise:** the concept with the *lowest* mastery whose
  prerequisites are already at **0.60** or higher. So a student struggling
  with loops keeps getting loops — they are not pushed into conditionals.
- **Difficulty** (1–3) steps **up** after 2 successes in a row and **down**
  after 2 failures in a row.

The same rule is implemented twice and must stay in sync:
`grader/recommend.py` (reference, tested) and `web/src/lib/recommend.ts`
(used by the UI for local progress).

## PWA
Installable manifest + service worker precaching static assets
(vite-plugin-pwa). Grading always needs the sandbox server — there is no
offline grading in v1.
