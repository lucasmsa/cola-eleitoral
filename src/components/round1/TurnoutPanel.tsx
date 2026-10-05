import { COPY } from '@/config/copy';
import type { TurnoutView } from '@/hooks/useRound1';
import { SourceLine } from './SourceLine';

export function TurnoutPanel({ items }: { items: TurnoutView[] }) {
  return (
    <section className="grid gap-4" aria-labelledby="turnout">
      <h2 id="turnout" className="text-3xl font-bold">
        {COPY.round1.turnout}
      </h2>
      <div className="grid gap-4 md:grid-cols-2">
        {items.map((t) => (
          <article key={t.scope} className="grid gap-2 rounded-md border-2 border-edge bg-paper p-4">
            <h3 className="text-xl font-bold">{t.scope}</h3>
            <ul className="grid gap-1 text-lg">
              {t.lines.map((l) => (
                <li key={l} className="tabular">
                  {l}
                </li>
              ))}
            </ul>
            {t.note && <p className="text-base text-muted">{t.note}</p>}
            <p className="text-base text-muted">{COPY.round1.turnoutNote}</p>
            <SourceLine source={t.source} />
          </article>
        ))}
      </div>
    </section>
  );
}
