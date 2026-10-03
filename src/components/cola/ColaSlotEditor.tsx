import { COPY } from '@/config/copy';
import type { ColaSlotView } from '@/hooks/useCola';
import { colaStatus, type ColaStatusKind } from '@/lib/colaStatus';
import { Button } from '../shell/ui';

interface Props {
  view: ColaSlotView;
  onType: (raw: string) => void;
  onBranco: () => void;
  onClear: () => void;
}

const STATUS_STYLE: Record<ColaStatusKind, string> = {
  ok: 'text-favor',
  warn: 'text-contra',
  idle: 'text-muted',
};

export function ColaSlotEditor({ view, onType, onBranco, onClear }: Props) {
  const id = `cola-${view.slot.id}`;
  const status = colaStatus(view.lookup, view.slot.digits);
  return (
    <li className="grid gap-2 rounded-md border-2 border-edge bg-paper p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <label htmlFor={id} className="text-xl font-bold">
          <span className="tabular mr-2 text-xl font-extrabold text-pen">{view.index + 1}</span>
          {view.slot.label}
        </label>
        <span className="text-base text-muted">{view.slot.digits} dígitos</span>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:items-center">
        <input
          id={id}
          inputMode="numeric"
          autoComplete="off"
          aria-describedby={`${id}-status`}
          value={view.digits}
          onChange={(e) => onType(e.target.value)}
          maxLength={view.slot.digits}
          placeholder={'0'.repeat(view.slot.digits)}
          style={{ width: `calc(${view.slot.digits} * 1.15em + 1.5rem)` }}
          className="tabular col-span-2 max-w-full justify-self-start rounded-md border-2 border-edge bg-white px-3 py-2 text-3xl font-bold tracking-[0.3em] text-ink placeholder:text-line focus:border-ink"
        />
        <Button size="sm" onClick={onBranco}>
          {COPY.cola.branco}
        </Button>
        <Button variant="quiet" size="sm" onClick={onClear}>
          {COPY.cola.clear}
        </Button>
      </div>
      <p id={`${id}-status`} className={`text-lg font-semibold ${STATUS_STYLE[status.kind]}`} aria-live="polite">
        {status.text}
      </p>
    </li>
  );
}
