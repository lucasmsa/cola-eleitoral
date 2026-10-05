import { COPY } from '@/config/copy';
import type { RowView } from '@/hooks/useRound2';
import { EvidenceLine } from '../lesson/EvidenceItem';
import { Disclosure } from '../shell/Disclosure';
import { ToneChip } from '../shell/ui';

export function ComparisonRow({ row }: { row: RowView }) {
  return (
    <li className="grid gap-3 rounded-md border-2 border-edge bg-paper p-4">
      <p className="text-xl font-bold">{row.question.statement}</p>
      <p className="text-lg">
        <b>{COPY.round2.you}:</b> <span className={row.answered ? '' : 'text-muted'}>{row.you}</span>
      </p>
      <div className="grid gap-3 md:grid-cols-2">
        {row.sides.map((s) => (
          <div key={s.finalistId} className="grid min-w-0 content-start gap-2 border-l-2 border-rule pl-3">
            <p className="flex flex-wrap items-center gap-2 text-lg">
              <b>{s.name}</b>
              {s.tone ? <ToneChip tone={s.tone}>{s.label}</ToneChip> : <span className="text-muted">{s.label}</span>}
            </p>
            {s.evidence.length > 0 && (
              <Disclosure look="dashed" summary={COPY.round2.sources(s.evidence.length)}>
                <ul className="grid gap-4 p-3">
                  {s.evidence.map((e) => (
                    <EvidenceLine key={e.id} evidence={e} />
                  ))}
                </ul>
              </Disclosure>
            )}
          </div>
        ))}
      </div>
    </li>
  );
}
