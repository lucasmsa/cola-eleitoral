import { useEffect } from 'react';
import type { RiveAsset } from '@/config/rive';
import { useRiveAsset } from './useRiveAsset';

export function useStamp(asset: RiveAsset) {
  const rive = useRiveAsset(asset);
  const { status, fire } = rive;
  useEffect(() => {
    if (status === 'ready') fire('stamp');
  }, [status, fire]);
  return rive;
}
