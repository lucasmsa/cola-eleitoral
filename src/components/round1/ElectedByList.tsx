import { COPY } from '@/config/copy';
import type { ListGroup } from '@/lib/round1';
import { formatInt } from '@/lib/round1';
import { titleCase } from '@/lib/text';
import { Portrait } from '../shell/Portrait';

interface Props {
  groups: ListGroup[];
  total: number;
  portraitOf: (candidateId: string) => string | null;
}

export function ElectedByList({ groups, total, portraitOf }: Props) {
  return (
    <div className="grid gap-5">
      {groups.map((g) => (
        <article key={g.list} className="grid gap-3 rounded-md border-2 border-edge bg-paper p-4">
          <header className="flex flex-wrap items-baseline justify-between gap-x-3">
            <h4 className="text-xl font-bold">{titleCase(g.list)}</h4>
            <span className="tabular text-lg font-semibold">{COPY.round1.seatsLine(g.seats, total)}</span>
          </header>
          {g.parties && g.parties !== g.list && <p className="text-base text-muted">{g.parties}</p>}
          <ul className="grid gap-3 sm:grid-cols-2">
            {g.people.map((p) => (
              <li key={p.candidateId} className="flex min-w-0 items-center gap-3">
                <Portrait name={p.ballotName} file={portraitOf(p.candidateId)} size="avatar" />
                <span className="grid min-w-0">
                  <span className="text-lg font-semibold">
                    {titleCase(p.ballotName)} <span className="tabular text-muted">{p.number}</span>
                  </span>
                  <span className="text-base text-muted">
                    {p.party}, {COPY.round1.votes(formatInt(p.votes))}, {p.how === 'QP' ? COPY.round1.howQP : COPY.round1.howMedia}
                  </span>
                </span>
              </li>
            ))}
          </ul>
        </article>
      ))}
    </div>
  );
}
