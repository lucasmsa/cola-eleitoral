import { COPY } from '@/config/copy';
import type { PickRow } from '@/lib/round1';
import { titleCase } from '@/lib/text';
import { Tag } from '../shell/ui';

export function YourVotes({ picks }: { picks: PickRow[] }) {
  if (picks.length === 0) return null;
  return (
    <section className="grid gap-3 rounded-md border-2 border-ink bg-fact p-4" aria-labelledby="your-votes">
      <h2 id="your-votes" className="text-3xl font-bold">
        {COPY.round1.yourVotes}
      </h2>
      <p className="text-lg text-muted">{COPY.round1.yourVotesLead}</p>
      <ul className="grid gap-2">
        {picks.map((p) => (
          <li key={p.slot} className="flex flex-wrap items-baseline justify-between gap-x-3 border-b border-rule pb-2">
            <span className="text-lg">
              <span className="font-semibold">{p.label}</span>
              {p.name && <>: {titleCase(p.name)}</>}
              {p.detail && <span className="text-muted"> ({p.detail})</span>}
            </span>
            <Tag strong={p.outcome === 'eleito' || p.outcome === 'segundo-turno'}>{COPY.round1.outcome[p.outcome]}</Tag>
          </li>
        ))}
      </ul>
    </section>
  );
}
