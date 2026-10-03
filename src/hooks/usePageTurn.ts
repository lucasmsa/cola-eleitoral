import { useEffect, useState } from 'react';
import { PAGE_TURN, PAGE_TURN_END_MS, PAGE_TURN_SWAP_MS } from '@/config/rive';
import type { Screen } from '@/stores/screen';
import { prefersReducedMotion, useRiveAsset } from './useRiveAsset';

export function screenKey(screen: Screen): string {
  if (screen.name === 'lesson') return `lesson:${screen.unitId}`;
  if (screen.name === 'results') return `results:${screen.step}`;
  return screen.name;
}

/** Holds the old screen until the paper sheet covers it, then swaps underneath. */
export function usePageTurn(screen: Screen) {
  const rive = useRiveAsset(PAGE_TURN);
  const { status, fire } = rive;
  const [shown, setShown] = useState(screen);
  const [turning, setTurning] = useState(false);
  const animated = status === 'ready' && !prefersReducedMotion();
  const key = screenKey(screen);
  const turnsPage = screenKey(shown).split(':')[0] !== key.split(':')[0];

  useEffect(() => {
    if (!animated || !turnsPage) {
      const sync = setTimeout(() => setShown(screen), 0);
      return () => clearTimeout(sync);
    }
    fire('turn');
    const start = setTimeout(() => setTurning(true), 0);
    const swap = setTimeout(() => setShown(screen), PAGE_TURN_SWAP_MS);
    const end = setTimeout(() => setTurning(false), PAGE_TURN_END_MS);
    return () => {
      clearTimeout(start);
      clearTimeout(swap);
      clearTimeout(end);
    };
    // The screen object is new on every navigation; its key is what matters.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, animated]);

  return { canvasRef: rive.canvasRef, displayed: animated && turnsPage ? shown : screen, turning, ready: status === 'ready' };
}
