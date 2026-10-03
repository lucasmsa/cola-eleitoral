import { COPY } from '@/config/copy';
import { useCola } from '@/hooks/useCola';
import { Button } from '../shell/ui';
import { ColaCard } from './ColaCard';
import { ColaSlotEditor } from './ColaSlotEditor';

export function ColaScreen() {
  const c = useCola();
  return (
    <>
      <main className="screen-only mx-auto grid max-w-5xl gap-6 px-4 py-6 md:pl-24">
        <h1 className="text-5xl font-extrabold">{COPY.cola.title}</h1>
        <p className="max-w-[65ch] text-xl text-muted">{COPY.cola.lead}</p>
        <p className="font-hand text-2xl text-pen">{COPY.cola.rules}</p>
        <div className="grid items-start gap-8 lg:grid-cols-[1fr_auto]">
          <ol className="grid min-w-0 gap-3">
            {c.views.map((v) => (
              <ColaSlotEditor
                key={v.slot.id}
                view={v}
                onType={(raw) => c.typeDigits(v.slot, raw)}
                onBranco={() => c.setBranco(v.slot)}
                onClear={() => c.clear(v.slot)}
              />
            ))}
          </ol>
          <div className="order-first grid min-w-0 justify-items-start gap-3 lg:order-none lg:sticky lg:top-24">
            <div className="max-w-full overflow-x-auto lg:overflow-visible lg:[zoom:1.3]">
              <ColaCard views={c.views} />
            </div>
            {c.sameSenator && <p className="max-w-sm rounded-md border-2 border-pen bg-pen-soft p-3 text-lg">{COPY.cola.sameSenator}</p>}
            <Button variant="primary" onClick={c.print}>
              {COPY.cola.print}
            </Button>
            <p className="max-w-sm text-base text-muted">{COPY.cola.printHint}</p>
            <Button variant="quiet" onClick={c.openResults}>
              {COPY.cola.toResults}
            </Button>
          </div>
        </div>
      </main>
      <div className="print-only">
        <ColaCard views={c.views} />
        <ColaCard views={c.views} />
      </div>
    </>
  );
}
