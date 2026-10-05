import { COPY } from '@/config/copy';
import { useRound2 } from '@/hooks/useRound2';
import { ColaCard } from '../cola/ColaCard';
import { ColaSlotEditor } from '../cola/ColaSlotEditor';
import { Button } from '../shell/ui';

export function Round2Cola() {
  const r = useRound2();
  return (
    <>
      <section className="grid gap-4" aria-labelledby="cola2">
        <h2 id="cola2" className="text-3xl font-bold">
          {COPY.round2.colaTitle}
        </h2>
        <p className="max-w-[65ch] text-lg text-muted">{COPY.round2.colaLead(r.numbers)}</p>
        <div className="grid items-start gap-6 lg:grid-cols-[1fr_auto]">
          <ol className="grid min-w-0 gap-3">
            {r.colaViews.map((v) => (
              <ColaSlotEditor
                key={v.slot.id}
                view={v}
                onType={(raw) => r.typeDigits(v.slot, raw)}
                onBranco={() => r.setBranco(v.slot)}
                onClear={() => r.clear(v.slot)}
                notFoundText={r.notFoundText}
              />
            ))}
          </ol>
          <div className="grid min-w-0 justify-items-start gap-3">
            <div className="max-w-full overflow-x-auto" data-testid="cola2-card">
              <ColaCard views={r.colaViews} title={r.colaTitle} note={r.colaNote} />
            </div>
            <Button variant="primary" onClick={r.print}>
              {COPY.cola.print}
            </Button>
            <p className="max-w-sm text-base text-muted">{COPY.cola.printHint}</p>
          </div>
        </div>
      </section>
    </>
  );
}

export function Round2ColaPrint() {
  const r = useRound2();
  return (
    <div className="print-only">
      <ColaCard views={r.colaViews} title={r.colaTitle} note={r.colaNote} />
      <ColaCard views={r.colaViews} title={r.colaTitle} note={r.colaNote} />
    </div>
  );
}
