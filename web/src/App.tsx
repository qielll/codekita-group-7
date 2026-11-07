import { useEffect, useMemo, useRef, useState } from "react";
import * as Blockly from "blockly";
import { pythonGenerator } from "blockly/python";
// Lesson/exercise content lives as data files under content/ (see MVP_SPEC §2) —
// loaded here via glob, never hardcoded.
const lessonModules = import.meta.glob("../../content/lessons/*.json", { eager: true, import: "default" });
const exerciseModules = import.meta.glob("../../content/exercises/*.json", { eager: true, import: "default" });
const lessonsData = Object.values(lessonModules) as LessonRaw[];
const exercisesData = Object.values(exerciseModules) as { concept: string; exercises: Exercise[] }[];
import { applyResult, loadProgress, recommend, saveProgress, type Progress } from "./lib/recommend";

type Exercise = { id: string; concept: string; difficulty: number; prompt: string; tests: { stdin: string; expected_stdout: string }[] };
type LessonRaw = { id: string; concept: string; title: string; explanation: string; example: { description: string; code: string; expected_stdout: string }; exercise_ids: string[] };
type Lesson = LessonRaw;
const allExercises: Exercise[] = exercisesData.flatMap((g) => g.exercises);
const GRADER_URL = import.meta.env.VITE_GRADER_URL ?? "http://localhost:8000";

const TOOLBOX = {
  kind: "categoryToolbox",
  contents: [
    { kind: "category", name: "Output", colour: "160", contents: [{ kind: "block", type: "text_print" }, { kind: "block", type: "text" }, { kind: "block", type: "math_number" }] },
    { kind: "category", name: "Loops", colour: "120", contents: [{ kind: "block", type: "controls_repeat_ext" }, { kind: "block", type: "controls_for" }] },
    { kind: "category", name: "Logic", colour: "210", contents: [{ kind: "block", type: "controls_if" }, { kind: "block", type: "logic_compare" }] },
    { kind: "category", name: "Variables", colour: "330", contents: [{ kind: "block", type: "variables_set" }, { kind: "block", type: "variables_get" }, { kind: "block", type: "math_arithmetic" }] },
  ],
};

export default function App() {
  const blocklyRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<Blockly.WorkspaceSvg | null>(null);
  const [lesson, setLesson] = useState<Lesson>(lessonsData[0]);
  const [exercise, setExercise] = useState<Exercise>(allExercises[0]);
  const [code, setCode] = useState("");
  const [feedback, setFeedback] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState<Progress>(loadProgress);

  useEffect(() => { saveProgress(progress); }, [progress]);

  useEffect(() => {
    if (!blocklyRef.current || wsRef.current) return;
    const ws = Blockly.inject(blocklyRef.current, { toolbox: TOOLBOX as never, trashcan: true });
    wsRef.current = ws;
    ws.addChangeListener(() => setCode(pythonGenerator.workspaceToCode(ws)));
    return () => { ws.dispose(); wsRef.current = null; };
  }, []);

  const recommendedConcept = useMemo(() => recommend(progress.mastery), [progress]);
  const pickExercise = (ex: Exercise) => {
    setExercise(ex);
    setLesson(lessonsData.find((l) => l.concept === ex.concept) ?? lesson);
    setFeedback("");
    wsRef.current?.clear();
  };

  async function grade() {
    setBusy(true); setFeedback("");
    try {
      const r = await fetch(`${GRADER_URL}/grade`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ code, exercise_id: exercise.id }) });
      if (!r.ok) throw new Error();
      const body = await r.json();
      setFeedback(body.summary + (body.sandbox === "local-dev" ? " (dev sandbox)" : ""));
      setProgress((p) => applyResult(p, exercise.concept, exercise.id, body.passed));
    } catch {
      setFeedback("Grader is not reachable. Start it with: uvicorn grader.main:app --port 8000 (Docker required for real sandboxing — see README).");
    } finally { setBusy(false); }
  }

  return (
    <div style={{ fontFamily: "system-ui", margin: 16, maxWidth: 1200 }}>
      <h1>CodeKita — Learn Python with Blocks</h1>
      <label>Your name or class code (no password):{" "}
        <input value={progress.profile} onChange={(e) => setProgress({ ...progress, profile: e.target.value })} placeholder="e.g. Siti / 5A" />
      </label>

      <div style={{ display: "flex", gap: 16, marginTop: 16, flexWrap: "wrap" }}>
        <aside style={{ width: 260 }}>
          <h2>Lessons</h2>
          {lessonsData.map((l) => (
            <button key={l.id} style={{ display: "block", width: "100%", textAlign: "left", marginBottom: 6, fontWeight: l.id === lesson.id ? 700 : 400 }}
              onClick={() => { setLesson(l); const ex = allExercises.find((e) => e.id === l.exercise_ids[0]); if (ex) pickExercise(ex); }}>
              {l.title}{recommendedConcept === l.concept ? " ⭐ recommended" : ""}
            </button>
          ))}
          <h3>{lesson.title}</h3>
          <p>{lesson.explanation}</p>
          <p><strong>Example:</strong> {lesson.example.description}</p>
          <pre style={{ background: "#f4f4f4", padding: 8 }}>{lesson.example.code}</pre>
          <h3>Exercises</h3>
          {allExercises.filter((e) => e.concept === lesson.concept).map((e) => (
            <button key={e.id} style={{ display: "block", width: "100%", textAlign: "left", marginBottom: 6 }}
              onClick={() => pickExercise(e)}>
              {progress.completed.includes(e.id) ? "✅ " : ""}Level {e.difficulty}: {e.prompt.slice(0, 60)}…
            </button>
          ))}
          <h3>Your progress</h3>
          {Object.entries(progress.mastery).map(([c, m]) => (
            <div key={c}>{c}: <progress value={m} max={1} /> {Math.round(m * 100)}%</div>
          ))}
          <p>Completed: {progress.completed.length}/{allExercises.length} · Next up: <strong>{recommendedConcept}</strong></p>
        </aside>

        <main style={{ flex: 1, minWidth: 320 }}>
          <h2>Exercise</h2>
          <p>{exercise.prompt}</p>
          <div ref={blocklyRef} style={{ height: 380, width: "100%" }} />
          <h3>Python preview (read-only)</h3>
          <pre style={{ background: "#111", color: "#eee", padding: 10, minHeight: 60 }}>{code || "# Drag blocks to build your program"}</pre>
          <button onClick={grade} disabled={busy || !code.trim()}>{busy ? "Grading…" : "Run & Grade"}</button>
          {feedback && <p role="status">{feedback}</p>}
        </main>
      </div>
    </div>
  );
}
