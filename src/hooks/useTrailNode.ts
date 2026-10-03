import { useEffect } from 'react';
import { TRAIL_NODE } from '@/config/rive';
import { useRiveAsset } from './useRiveAsset';

export function useTrailNode(progress: number, done: boolean) {
  const rive = useRiveAsset(TRAIL_NODE);
  const { status, setNumber, setBoolean } = rive;
  useEffect(() => {
    if (status !== 'ready') return;
    setNumber('progress', Math.round(progress * 100));
    setBoolean('done', done);
  }, [status, progress, done, setNumber, setBoolean]);
  return rive;
}
