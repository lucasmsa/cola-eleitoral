import { useMemo } from 'react';
import { meta, questions } from '@/data';
import { buildUnits, unitProgress } from '@/lib/lessons';
import { useAnswersStore } from '@/stores/answers';
import { useTurnoStore } from '@/stores/turno';
import { useNav } from './useNav';

export function useHome() {
  const answers = useAnswersStore((s) => s.answers);
  const turno = useTurnoStore((s) => s.turno);
  const nav = useNav();
  const units = useMemo(() => buildUnits(questions), []);
  const rows = units.map((unit) => ({ unit, progress: unitProgress(unit, answers) }));
  const answered = rows.reduce((n, r) => n + r.progress.answered, 0);
  const total = rows.reduce((n, r) => n + r.progress.total, 0);
  const nextUnit = rows.find((r) => r.progress.answered < r.progress.total)?.unit ?? null;
  return {
    turno,
    rows,
    answered,
    total,
    nextUnit,
    allDone: total > 0 && answered === total,
    factCount: meta.evidence,
    builtAt: meta.builtAt,
    openUnit: nav.goLesson,
    openResults: nav.goResults,
    openReview: nav.goReview,
    openCola: nav.goCola,
  };
}
