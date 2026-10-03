import { COPY } from '@/config/copy';
import type { ColaSlotId } from '@/config/election';
import type { ResultRow } from '@/lib/rows';
import { Disclosure } from '../shell/Disclosure';
import { ScoreRow } from './ScoreRow';

const TOP = 5;

interface Props {
  rows: { scored: ResultRow[]; unscored: ResultRow[] };
  colaSlotOf: (row: ResultRow) => ColaSlotId | null;
  slotsFull: boolean;
  onPut: (row: ResultRow) => void;
  onRemove: (slot: ColaSlotId) => void;
  onDetails: (row: ResultRow) => void;
  onOpenList?: (id: string) => void;
}

export function RankingList({ rows, ...handlers }: Props) {
  const top = rows.scored.slice(0, TOP);
  const rest = rows.scored.slice(TOP);
  return (
    <div className="grid gap-3">
      <ol className="grid gap-3">
        {top.map((row, i) => (
          <ScoreRow key={row.id} rank={i + 1} row={row} {...handlers} />
        ))}
      </ol>
      {rest.length > 0 && (
        <Disclosure summary={COPY.results.showRest(rest.length)}>
          <ol className="grid gap-3" start={TOP + 1}>
            {rest.map((row, i) => (
              <ScoreRow key={row.id} rank={TOP + i + 1} row={row} {...handlers} />
            ))}
          </ol>
        </Disclosure>
      )}
      {rows.unscored.length > 0 && (
        <Disclosure look="dashed" summary={`${COPY.results.unscored} (${rows.unscored.length})`}>
          <p className="text-lg text-muted">{COPY.results.unscoredExplain}</p>
          <ul className="mt-3 grid gap-3">
            {rows.unscored.map((row) => (
              <ScoreRow key={row.id} rank={null} row={row} {...handlers} />
            ))}
          </ul>
        </Disclosure>
      )}
    </div>
  );
}
