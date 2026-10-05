import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { candidates, meta, polls, polls2, round1, round2 } from '@/data';
import { COPY } from '@/config/copy';
import { dataFreshness } from '@/lib/freshness';

export function useDataInfo() {
  const [open, setOpen] = useState(false);
  const id = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const freshness = useMemo(
    () =>
      dataFreshness({
        candidates,
        results: [round1, round2],
        builtAt: meta.builtAt,
        polls: [...polls, ...polls2],
        officeLabel: (o) => COPY.dataInfo.pollOffice[o] ?? o,
      }),
    [],
  );

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return;
      setOpen(false);
      buttonRef.current?.focus();
    };
    const onPointer = (e: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('keydown', onKey);
    document.addEventListener('pointerdown', onPointer);
    return () => {
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('pointerdown', onPointer);
    };
  }, [open]);

  return { open, panelId: `${id}-data-info`, rootRef, buttonRef, freshness, toggle: () => setOpen((v) => !v) };
}
