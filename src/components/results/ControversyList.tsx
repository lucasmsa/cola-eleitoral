import { COPY } from '@/config/copy';
import type { Controversy } from '@/data/schema';
import { CATEGORY_LABEL } from '@/lib/controversies';
import { brDate } from '@/lib/text';
import { Fonte } from './Fonte';

export function ControversyList({ items }: { items: Controversy[] }) {
  if (items.length === 0) return <p className="text-lg text-muted">{COPY.profile.noControversy}</p>;
  return (
    <ul className="grid gap-4">
      {items.map((c) => (
        <li key={c.id} className="grid gap-2 border-l-2 border-ink pl-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-sm border-2 border-ink bg-paper px-2 py-0.5 text-base font-extrabold uppercase tracking-wide text-ink">{c.status}</span>
            <span className="text-base text-muted">
              {CATEGORY_LABEL[c.category]}, {brDate(c.date)}
            </span>
          </div>
          <p className="text-lg font-bold leading-snug">{c.title}</p>
          {c.claims.map((cl) => (
            <p key={cl.checkId} className="text-lg leading-snug">
              {cl.text}
              <Fonte url={cl.source.url} label={cl.source.label} />
            </p>
          ))}
          {c.response.length > 0 && (
            <div className="grid gap-1 rounded-md bg-fact p-3">
              <p className="text-base font-bold">{COPY.profile.response}</p>
              {c.response.map((r) => (
                <p key={r.checkId} className="text-lg leading-snug">
                  {r.text}
                  <Fonte url={r.source.url} label={r.source.label} />
                </p>
              ))}
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}
