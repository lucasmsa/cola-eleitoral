import { COPY } from '@/config/copy';
import type { Endorsement } from '@/data/schema';
import { SourceLink, Tag } from '../shell/ui';

export function Endorsements({ items }: { items: Endorsement[] }) {
  if (items.length === 0) return null;
  return (
    <section className="grid gap-4" aria-labelledby="endorsements">
      <div className="grid gap-1">
        <h2 id="endorsements" className="text-3xl font-bold">
          {COPY.round2.endorsementsTitle}
        </h2>
        <p className="max-w-[65ch] text-lg text-muted">{COPY.round2.endorsementsLead}</p>
      </div>
      <ul className="grid gap-4 md:grid-cols-2">
        {items.map((e) => (
          <li key={e.id} className="grid content-start gap-2 rounded-md border-2 border-edge bg-paper p-4">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="text-xl font-bold">{e.who}</h3>
              <Tag>{e.supports}</Tag>
            </div>
            {e.claims.map((c) => (
              <div key={c.checkId} className="grid gap-1">
                <p className="text-lg">{c.text}</p>
                <blockquote className="border-l-4 border-rule pl-3 text-base text-muted">“{c.support}”</blockquote>
                <p className="text-base text-muted">
                  <SourceLink label={c.source.label} url={c.source.url} />
                </p>
              </div>
            ))}
          </li>
        ))}
      </ul>
    </section>
  );
}
