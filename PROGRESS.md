# PROGRESS

## Status: MVP complete (all 4 milestones) — 2026-11-08

- [x] M1 Grader only — `POST /grade` pass/fail per hidden test case, Docker
      sandbox (network off, CPU/mem/pids limits, 2 s timeout, non-root),
      infinite loop killed as a timeout, friendly feedback only.
- [x] M2 Blocks → Python — Blockly workspace, restricted palette
      (Output / Loops / Logic / Variables), built-in Python generator,
      live read-only Python preview.
- [x] M3 Loop closed — web UI submits generated Python to `/grade` and
      shows the summary; grader-offline state shows how to start it.
- [x] M4 Adaptivity + progress — BKT mastery per concept (see
      ARCHITECTURE.md), lowest-mastery-with-prereqs-met recommendation,
      difficulty ± after 2-in-a-row, progress view with mastery bars,
      local profile (name/class code), progress in localStorage, PWA
      manifest + service worker.

## Content
4 lessons (sequences, loops, conditionals, variables), 10 exercises.

## Verification (2026-11-08, this build VM)
- `pytest tests/ -q` → **8 passed** (grader pass/fail/timeout/no-stack-trace,
  all 4 worked examples produce their expected output, BKT + recommendation).
- End-to-end script: correct solutions for **all 10 exercises pass**
  through `/grade`; full lesson path completable.
- `web: npm run build` → succeeds (tsc + Vite + PWA precache generated).

## Known gap — read before the demo
- ⚠️ **Docker was not available in the build VM** (`docker: command not
  found`), so the tests above ran through the explicit dev-only local
  sandbox (`CODEKITA_ALLOW_LOCAL_SANDBOX=1`, timeout + rlimits, reported
  as `sandbox: "local-dev"` in responses). The Docker runner path is
  implemented per spec but **not yet live-verified**. Before any demo:
  build `codekita-sandbox:latest`, run the grader *without* the env var,
  and re-run `pytest` + the infinite-loop check, confirming responses say
  `sandbox: "docker"`.

## Deferred to v2 (per MVP_SPEC §3)
Teacher dashboard, real auth, IRT/ML recommendation, LLM tutoring,
native apps, offline grading, more than 5 lessons.
