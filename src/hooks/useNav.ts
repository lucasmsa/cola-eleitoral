import type { ResultStep } from '@/config/result';
import { useScreenStore } from '@/stores/screen';

export function useNav() {
  const screen = useScreenStore((s) => s.screen);
  const go = useScreenStore((s) => s.go);
  return {
    screen,
    goHome: () => go({ name: 'home' }),
    goLesson: (unitId: string) => go({ name: 'lesson', unitId }),
    goResults: () => go({ name: 'results', step: 'alinhamento' }),
    goResultStep: (step: ResultStep) => go({ name: 'results', step }),
    goReview: () => go({ name: 'review' }),
    goCola: () => go({ name: 'cola' }),
  };
}
