import { RESULT_STEPS, type ResultStep } from '@/config/result';
import { useAnswersStore } from '@/stores/answers';
import { useNav } from './useNav';

export function useResultFlow() {
  const nav = useNav();
  const step: ResultStep = nav.screen.name === 'results' ? nav.screen.step : 'alinhamento';
  const index = Math.max(0, RESULT_STEPS.findIndex((s) => s.id === step));
  const prev = RESULT_STEPS[index - 1] ?? null;
  const next = RESULT_STEPS[index + 1] ?? null;
  const answered = useAnswersStore((s) => Object.values(s.answers).filter((a) => a !== 'skip').length);
  return {
    steps: RESULT_STEPS,
    step,
    index,
    current: RESULT_STEPS[index]!,
    prev,
    next,
    answered,
    go: nav.goResultStep,
    goPrev: () => prev && nav.goResultStep(prev.id),
    goNext: () => (next ? nav.goResultStep(next.id) : nav.goCola()),
    goCola: nav.goCola,
  };
}
