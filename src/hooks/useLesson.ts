import { useCallback, useEffect, useMemo, useState } from 'react';
import { DEFAULT_IMPORTANCE } from '@/config/answers';
import { RECORDED_MS, RECORDED_REDUCED_MS } from '@/config/rive';
import { explainers, questions } from '@/data';
import { explainerFor } from '@/lib/explainers';
import { buildUnits, firstOpenIndex } from '@/lib/lessons';
import type { Importance, Stance } from '@/lib/score';
import { useAnswersStore } from '@/stores/answers';
import { useNav } from './useNav';
import { prefersReducedMotion } from './useRiveAsset';

export type LessonPhase = 'answer' | 'recorded' | 'done';

export function useLesson(unitId: string) {
  const units = useMemo(() => buildUnits(questions), []);
  const unit = units.find((u) => u.id === unitId) ?? units[0];
  const answers = useAnswersStore((s) => s.answers);
  const setAnswer = useAnswersStore((s) => s.setAnswer);
  const nav = useNav();
  const [index, setIndex] = useState(() => (unit ? firstOpenIndex(unit, answers) : 0));
  const [phase, setPhase] = useState<LessonPhase>(() =>
    unit && firstOpenIndex(unit, answers) >= unit.questions.length ? 'done' : 'answer',
  );
  const [stance, setStance] = useState<Stance | null>(null);
  const [importance, setImportance] = useState<Importance>(DEFAULT_IMPORTANCE);
  const [explainerOpen, setExplainerOpen] = useState(true);
  const [nods, setNods] = useState(0);

  const total = unit?.questions.length ?? 0;
  const question = unit?.questions[Math.min(index, total - 1)] ?? null;
  const nextUnit = units[units.findIndex((u) => u.id === unit?.id) + 1] ?? null;
  const explainer = question ? explainerFor(explainers, question.id) : null;

  const advance = useCallback(() => {
    if (index + 1 >= total) {
      setStance(null);
      setImportance(DEFAULT_IMPORTANCE);
      setPhase('done');
      return;
    }
    const nextId = unit?.questions[index + 1]?.id;
    const saved = nextId ? answers[nextId] : undefined;
    setStance(saved && saved !== 'skip' ? saved.stance : null);
    setImportance(saved && saved !== 'skip' ? saved.importance : DEFAULT_IMPORTANCE);
    setIndex(index + 1);
    setPhase('answer');
  }, [index, total, unit, answers]);

  useEffect(() => {
    if (phase !== 'recorded' || import.meta.env.MODE === 'test') return;
    const wait = prefersReducedMotion() ? RECORDED_REDUCED_MS : RECORDED_MS;
    const t = setTimeout(advance, wait);
    return () => clearTimeout(t);
  }, [phase, advance]);

  function record(answer: Parameters<typeof setAnswer>[1]) {
    if (!question) return;
    setAnswer(question.id, answer);
    setNods((n) => n + 1);
    setPhase('recorded');
  }

  function confirm() {
    if (stance === null) return;
    record({ stance, importance });
  }

  function loadSaved(i: number) {
    const id = unit?.questions[i]?.id;
    const saved = id ? answers[id] : undefined;
    setStance(saved && saved !== 'skip' ? saved.stance : null);
    setImportance(saved && saved !== 'skip' ? saved.importance : DEFAULT_IMPORTANCE);
  }

  function back() {
    const target = phase === 'done' ? total - 1 : index - 1;
    if (target < 0) return;
    loadSaved(target);
    setIndex(target);
    setPhase('answer');
  }

  function restart() {
    setIndex(0);
    setStance(null);
    setImportance(DEFAULT_IMPORTANCE);
    setPhase('answer');
  }

  const answeredHere = phase === 'answer' ? index : index + 1;

  return {
    unit,
    question,
    explainer,
    explainerOpen,
    setExplainerOpen,
    nods,
    position: Math.min(index + 1, total),
    total,
    progress: total === 0 ? 0 : (phase === 'done' ? total : answeredHere) / total,
    phase,
    stance,
    importance,
    saved: question ? answers[question.id] : undefined,
    nextUnit,
    chooseStance: setStance,
    chooseImportance: setImportance,
    confirm,
    dontKnow: () => record('skip'),
    next: advance,
    back,
    canGoBack: phase === 'done' ? total > 0 : phase === 'answer' && index > 0,
    restart,
    exit: nav.goHome,
    openNextUnit: () => nextUnit && nav.goLesson(nextUnit.id),
    openResults: nav.goResults,
  };
}
