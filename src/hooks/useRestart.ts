import { useState } from 'react';
import { useAnswersStore } from '@/stores/answers';
import { useNav } from './useNav';

export function useRestart() {
  const [asking, setAsking] = useState(false);
  const resetAll = useAnswersStore((s) => s.resetAll);
  const nav = useNav();
  return {
    asking,
    ask: () => setAsking(true),
    cancel: () => setAsking(false),
    confirm: () => {
      resetAll();
      setAsking(false);
      nav.goHome();
    },
  };
}
