import { COPY } from '@/config/copy';
import type { MethodRow } from '@/hooks/useAlignment';
import { Disclosure } from '../shell/Disclosure';
import { Tag } from '../shell/ui';

interface Props {
  groups: { axis: string; label: string; rows: MethodRow[] }[];
  minPerAxis: number;
}

export function MethodDrawer({ groups, minPerAxis }: Props) {
  return (
    <Disclosure
      summary={
        <>
          {COPY.alignment.methodTitle} <Tag strong>{COPY.alignment.methodTag}</Tag>
        </>
      }
    >
      <div className="grid gap-5">
        {COPY.alignment.methodBody(minPerAxis).map((p) => (
          <p key={p} className="max-w-[70ch] text-lg">
            {p}
          </p>
        ))}
        {groups.map((g) => (
          <section key={g.axis} className="grid gap-2">
            <h3 className="text-2xl font-bold">{g.label}</h3>
            {g.rows.length === 0 && (
              <p className="text-lg text-muted">{COPY.alignment.noAxisRows}</p>
            )}
            <ul className="grid gap-3">
              {g.rows.map((r) => (
                <li key={r.questionId} className="grid gap-1 border-l-2 border-line pl-3">
                  <p className="text-lg font-semibold">{r.statement}</p>
                  <p className="font-hand text-xl text-pen">{r.direction}</p>
                  <p className="text-base text-muted">{r.rationale}</p>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </Disclosure>
  );
}
