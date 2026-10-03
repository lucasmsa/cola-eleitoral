import { useEffect, useRef } from 'react';
import { MASCOT, MOOD, type Mood } from '@/config/mascot';
import { useRiveAsset } from './useRiveAsset';

export function useMascot(mood: Mood, nodKey = 0) {
  const rive = useRiveAsset(MASCOT);
  const { status, setNumber, fire } = rive;
  const firstNod = useRef(nodKey);

  useEffect(() => {
    if (status !== 'ready') return;
    setNumber('mood', MOOD.idle);
    if (mood === 'idle') return;
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setNumber('mood', MOOD[mood])));
    return () => cancelAnimationFrame(id);
  }, [mood, status, setNumber]);

  useEffect(() => {
    if (status !== 'ready' || nodKey === firstNod.current) return;
    fire('nod');
  }, [nodKey, status, fire]);

  return rive;
}
