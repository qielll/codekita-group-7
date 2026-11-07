// TS port of grader/recommend.py — same BKT rule, documented in ARCHITECTURE.md.
export const P_INIT = 0.1, P_GUESS = 0.2, P_SLIP = 0.1, P_LEARN = 0.15;
export const PREREQS: Record<string, string[]> = {
  sequences: [], loops: ["sequences"], conditionals: ["loops"], variables: ["conditionals"],
};
export const CONCEPTS = Object.keys(PREREQS);

export function updateMastery(mastery: number, correct: boolean): number {
  const p = Math.min(Math.max(mastery, 0), 1);
  const post = correct
    ? (p * (1 - P_SLIP)) / (p * (1 - P_SLIP) + (1 - p) * P_GUESS)
    : (p * P_SLIP) / (p * P_SLIP + (1 - p) * (1 - P_GUESS));
  return post + (1 - post) * P_LEARN;
}

export function recommend(mastery: Record<string, number>): string {
  const sorted = [...CONCEPTS].sort((a, b) => (mastery[a] ?? P_INIT) - (mastery[b] ?? P_INIT));
  for (const c of sorted) {
    const prereqsMet = PREREQS[c].every((p) => (mastery[p] ?? P_INIT) >= 0.6);
    if (prereqsMet && (mastery[c] ?? P_INIT) < 0.95) return c;
  }
  return "variables";
}

export type Progress = {
  profile: string;
  mastery: Record<string, number>;
  completed: string[]; // exercise ids
  streakCorrect: number;
  streakWrong: number;
  difficulty: number;
};

const KEY = "codekita-progress-v1";
export function loadProgress(): Progress {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* fresh start */ }
  return { profile: "", mastery: Object.fromEntries(CONCEPTS.map((c) => [c, P_INIT])),
           completed: [], streakCorrect: 0, streakWrong: 0, difficulty: 1 };
}
export function saveProgress(p: Progress) { localStorage.setItem(KEY, JSON.stringify(p)); }

export function applyResult(p: Progress, concept: string, exerciseId: string, passed: boolean): Progress {
  const next = { ...p, mastery: { ...p.mastery } };
  next.mastery[concept] = updateMastery(next.mastery[concept] ?? P_INIT, passed);
  next.streakCorrect = passed ? p.streakCorrect + 1 : 0;
  next.streakWrong = passed ? 0 : p.streakWrong + 1;
  if (next.streakCorrect >= 2) { next.difficulty = Math.min(3, p.difficulty + 1); next.streakCorrect = 0; }
  if (next.streakWrong >= 2) { next.difficulty = Math.max(1, p.difficulty - 1); next.streakWrong = 0; }
  if (passed && !next.completed.includes(exerciseId)) next.completed = [...next.completed, exerciseId];
  return next;
}
