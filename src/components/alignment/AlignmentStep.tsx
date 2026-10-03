import { KIND_LABELS } from '@/config/alignment';
import { COPY } from '@/config/copy';
import { useAlignment } from '@/hooks/useAlignment';
import type { EntityKind } from '@/lib/alignment';
import { Portrait } from '../shell/Portrait';
import { AlignedLists } from './AlignedLists';
import { AlignmentChart } from './AlignmentChart';
import { MethodDrawer } from './MethodDrawer';
import { YouHiddenNotice } from './YouHiddenNotice';

export function AlignmentStep() {
  const a = useAlignment();
  return (
    <div className="grid min-w-0 grid-cols-[minmax(0,1fr)] gap-6">
      <p className="max-w-[70ch] text-lg">{COPY.alignment.lead}</p>
      {!a.hasAxes && <p className="rounded-md border-2 border-dashed border-edge p-4 text-lg text-muted">{COPY.alignment.noAxes}</p>}
      {a.hasAxes && (
        <section className="grid justify-items-start gap-3" aria-labelledby="chart-title">
          <h2 id="chart-title" className="text-3xl font-bold">
            {COPY.alignment.chartTitle}
          </h2>
          <div className="flex flex-wrap gap-2" role="group" aria-label={COPY.alignment.filters}>
            {(Object.keys(KIND_LABELS) as EntityKind[]).map((kind) => (
              <button
                key={kind}
                type="button"
                aria-pressed={a.shown[kind]}
                onClick={() => a.toggle(kind)}
                className={`inline-flex min-h-11 items-center rounded-full border-2 px-4 text-base font-semibold ${a.shown[kind] ? 'border-ink bg-ink text-paper' : 'border-edge bg-paper text-ink hover:bg-fact'}`}
              >
                {KIND_LABELS[kind]}
              </button>
            ))}
          </div>
          {!a.youVisible && <YouHiddenNotice minPerAxis={a.minPerAxis} have={{ x: a.you.x.n, y: a.you.y.n }} />}
          <AlignmentChart dots={a.dots} focusedId={a.focusedDot?.id ?? null} onFocus={a.focus} />
          <div className="flex min-h-[3.5rem] max-w-[70ch] items-center gap-3" aria-live="polite">
            {a.focusedDot?.kind === 'politico' && <Portrait name={a.focusedDot.label} file={a.focusedDot.portrait ?? null} size="chip" />}
            <p className="text-lg">
              {a.focusedDot ? COPY.alignment.focused(a.focusedDot.label, a.focusedDot.detail, a.focusedDot.placement.x.n, a.focusedDot.placement.y.n) : COPY.alignment.hint}
            </p>
          </div>
          <p className="text-base text-muted">{COPY.alignment.legend}</p>
          {a.hiddenByKind.length > 0 && (
            <p className="max-w-[70ch] text-lg" data-testid="hidden-dots">
              {COPY.alignment.hidden(a.hiddenByKind.map((h) => COPY.alignment.kindCount(h.kind, h.n)), a.minPerAxis)}
            </p>
          )}
          <MethodDrawer groups={a.method} minPerAxis={a.minPerAxis} />
        </section>
      )}
      <AlignedLists ranked={a.ranked} />
    </div>
  );
}
