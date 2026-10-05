import { COPY } from '@/config/copy';
import type { Poll } from '@/data/schema';
import { Disclosure } from '../shell/Disclosure';
import { brDate, brNumber, hostname, pollValue } from '@/lib/text';
import { SourceLink, Tag } from '../shell/ui';

interface Props {
  polls: Poll[];
  title?: string;
  explain?: string;
  caption?: (poll: Poll) => string;
}

export function PollPanel({ polls, title = COPY.polls.title, explain = COPY.polls.explain, caption }: Props) {
  return (
    <Disclosure summary={<>{title}</>}>
      <div className="grid gap-5">
        <p className="max-w-[70ch] text-lg text-muted">{explain}</p>
        {polls.length === 0 && <p className="text-lg text-muted">{COPY.polls.none}</p>}
        {polls.map((p) => (
          <article key={p.id} className="grid gap-2">
            <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
              <h3 className="text-2xl font-bold">{p.institute}</h3>
              <span className="tabular text-base text-muted">
                campo {brDate(p.fieldStart)} a {brDate(p.fieldEnd)},{' '}
                {p.sample.toLocaleString('pt-BR')} entrevistas, margem de {brNumber(p.marginPp)}{' '}
                pontos, registro {p.registration}
              </span>
              <Tag>{COPY.polls.pressChecked}</Tag>
            </div>
            {caption && <p className="text-lg font-semibold">{caption(p)}</p>}
            <ul className="grid gap-1 sm:grid-cols-2">
              {p.results.map((r) => (
                <li
                  key={r.label}
                  className="flex justify-between gap-3 border-b border-rule text-lg"
                >
                  <span>{r.label}</span>
                  <span className="tabular font-semibold">{pollValue(r.pct)}</span>
                </li>
              ))}
            </ul>
            <p className="text-base text-muted">
              Fonte: <SourceLink label={hostname(p.source.url)} url={p.source.url} />
            </p>
          </article>
        ))}
      </div>
    </Disclosure>
  );
}
