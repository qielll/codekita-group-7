# MVP Spec — CodeKita

**Source:** Capstone.docx, Teknik Informatika #3 — Platform Pembelajaran Pemrograman Dasar Adaptif untuk Pelajar
**Repo:** `codekita` (separate repo, separate chat — do not mix with the other 3 capstone projects)
**Difficulty:** 4/5 · **Token estimate:** ~600k–1.2M

## 1. Goal — the one demo loop

A student opens the web app → drags visual blocks to solve a small programming task → the blocks convert to Python → the code is auto-graded safely → the student gets a score/feedback → the next recommended task is slightly harder or easier based on their mastery.

If this loop works for a short lesson path in the demo, the MVP succeeds.

## 2. IN scope (v1)

### Learning content
- **3–5 lessons only**, one concept each, for SD–SMA level computational thinking. Suggested path: sequences → loops → conditionals → variables → (optional) functions.
- Each lesson: short explanation, 1 worked example, 2–3 exercises.
- Content stored as data files (JSON/Markdown), not hardcoded in UI components, so lessons can be added without code changes.

### Block editor + transpiler
- Blockly editor in the browser, with a **restricted block palette** matching the lessons (motion/logic basics: sequence, loop, if, variable, print/output).
- Python code generation uses **Blockly's built-in Python generator** plus custom generators only for custom blocks. Do not write a transpiler from scratch.
- Live Python preview panel (read-only) so students see blocks → code.

### Auto-grader (core engine — build and test this first, alone)
- API endpoint: `POST /grade` with `{ code, exercise_id }` → runs the code in an **isolated Docker container** with hard limits: no network, CPU/time limit (e.g. 2s), memory limit, fresh container or equivalent isolation per run.
- Grading compares program output (stdout) against expected output for hidden test cases defined per exercise. Returns pass/fail per case + a friendly summary, never a raw stack trace to the student (log it server-side).
- The grader must reject/handle infinite loops and oversized output via the limits above — that is a feature of the capstone, demonstrate it.

### Adaptive recommendation
- Track per-concept mastery per student (simple model in v1): each concept has a mastery score updated from exercise results.
- Implement **simple Bayesian Knowledge Tracing or an equivalent documented rule-based update** (e.g. mastery increases on correct, decreases on incorrect, with a learning-rate parameter). Full Item Response Theory is out.
- Recommendation rule: next exercise = lowest-mastery concept whose prerequisites are met; difficulty steps up after consecutive successes, down after consecutive failures. The rule must be written down in `ARCHITECTURE.md` in plain language.

### App shell
- Web app (works in a desktop browser; mobile-responsive enough to not break).
- Student identity: simple local profile / class code — **no real account system, no passwords for children in v1**. Progress stored server-side keyed by that profile, or in local storage if the backend is cut — pick one in milestone 1 and document it.
- Progress view: lessons completed, per-concept mastery bars.
- PWA basics: installable manifest + cached static assets. True offline grading is out (grading needs the sandbox server).

### Repo hygiene
- `README.md`: how to run the app + grader (Docker required), how to add a lesson, demo script.
- `.gitignore`: `node_modules`, build output, Python venv/cache, local progress data.
- Tests: grader tests (correct solution passes, wrong solution fails, infinite loop times out safely), recommendation-rule tests with simulated results.

## 3. OUT of scope (v1) — do not build, do not let scope creep

- Native mobile apps (web/PWA only)
- Full Item Response Theory, ML-based recommendation, LLM tutoring/chat
- Teacher dashboard, class management, parent reports, leaderboards, certificates
- Real authentication, payments, multi-school tenancy
- Free-form Python editor as the main mode (blocks are the product; a read-only code view is enough)
- Offline code execution, offline-first sync conflict handling
- More than 5 lessons — content volume is not the technical contribution

## 4. Frozen stack

- Frontend: TypeScript + React (or plain Vite + TypeScript if React slows the build down — decide in milestone 1, then freeze), Blockly
- Grader/backend: Python 3 + FastAPI, Docker for sandboxed execution
- Data: JSON files for lessons/exercises; simple SQLite or local storage for progress (no external database server)
- If a choice is not listed here, pick the simplest option and note it in `ARCHITECTURE.md`.

## 5. Suggested repo structure

```
codekita/
  MVP_SPEC.md          <- this file, copied into the repo root
  ARCHITECTURE.md      <- includes the adaptive rule in plain language
  PROGRESS.md
  README.md
  .gitignore
  content/
    lessons/*.json
    exercises/*.json   <- includes hidden test cases
  web/
    src/ (Blockly workspace, Python preview, progress view)
    public/ (PWA manifest, icons)
  grader/
    main.py            <- FastAPI /grade endpoint
    runner.py          <- Docker sandbox execution with limits
    Dockerfile
  tests/
    test_grader.py
    test_recommend.py
```

## 6. Milestones (in order)

1. **Grader only:** `/grade` passes/fails sample solutions correctly and kills an infinite loop within the time limit.
2. **Blocks → Python:** Blockly workspace with the restricted palette generates correct Python for the lesson examples.
3. **Loop closed:** exercise submission from the web UI is graded and feedback is shown.
4. **Adaptivity + progress:** mastery tracking + next-exercise recommendation follow the documented rule; progress view; README demo script.

## 7. Acceptance criteria

- [ ] A correct block solution passes grading; a wrong one fails with friendly feedback (no stack traces shown)
- [ ] An infinite-loop submission is terminated by the sandbox limit and reported as a timeout, server stays alive
- [ ] Generated Python for each worked example matches the expected output when run
- [ ] After a simulated student fails a concept repeatedly, the recommendation steps down / repeats that concept; after repeated success, it steps up — demonstrated by tests
- [ ] Full lesson path (lesson 1 → final exercise) is completable in the demo without developer intervention

## 8. Risks & dependencies

- Docker must be available wherever the grader is demoed — state this in the README prerequisites; there is no non-Docker fallback in v1.
- Blockly custom blocks are fiddly — keep the palette minimal; every custom block needs a Python generator and a test.
- Sandbox security is a graded technical claim of this capstone: never execute student code on the host process, even "temporarily for the demo".

## 9. Context rules for whoever builds this

- This file is the scope contract. Anything in §3 is refused or deferred to a v2 note in `PROGRESS.md`.
- Lesson content files are data — load one at a time when needed, not the whole content folder.
- After each milestone, summarise state in `PROGRESS.md` so a fresh chat can continue from the files alone.
