import { COPY } from '@/config/copy';
import type { Turno } from '@/stores/turno';

const OPTIONS: { value: Turno; long: string; short: string }[] = [
  { value: 1, long: COPY.turno.one, short: COPY.turno.oneShort },
  { value: 2, long: COPY.turno.two, short: COPY.turno.twoShort },
];

export function TurnoSwitch({ turno, onChoose }: { turno: Turno; onChoose: (t: Turno) => void }) {
  return (
    <div role="group" aria-label={COPY.turno.label} className="inline-flex rounded-md border-2 border-ink p-0.5">
      {OPTIONS.map((o) => (
        <button
          key={o.value}
          type="button"
          aria-pressed={turno === o.value}
          aria-label={o.long}
          onClick={() => onChoose(o.value)}
          className={`min-h-10 min-w-10 rounded-sm px-1.5 text-base font-bold sm:px-2 md:px-3 ${turno === o.value ? 'bg-ink text-paper' : 'text-ink hover:bg-fact'}`}
        >
          <span className="xl:hidden">{o.short}</span>
          <span className="hidden xl:inline">{o.long}</span>
        </button>
      ))}
    </div>
  );
}
