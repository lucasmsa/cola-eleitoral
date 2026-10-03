import { COPY } from '@/config/copy';
import { COLA_SLOTS, type ColaSlotId } from '@/config/election';
import type { ResultRow } from '@/lib/rows';
import { percent } from '@/lib/text';
import { Portrait } from '../shell/Portrait';
import { Button, Tag } from '../shell/ui';
import { ScoreBand } from './ScoreBand';

interface Props {
  rank: number | null;
  row: ResultRow;
  colaSlotOf: (row: ResultRow) => ColaSlotId | null;
  slotsFull: boolean;
  onPut: (row: ResultRow) => void;
  onRemove: (slot: ColaSlotId) => void;
  onDetails: (row: ResultRow) => void;
  onOpenList?: (id: string) => void;
}

const SLOT_LABEL = Object.fromEntries(COLA_SLOTS.map((s) => [s.id, s.label])) as Record<ColaSlotId, string>;

export function ScoreRow({ rank, row, colaSlotOf, slotsFull, onPut, onRemove, onDetails, onOpenList }: Props) {
  const slot = colaSlotOf(row);
  const s = row.score;
  return (
    <li className="grid grid-cols-[2rem_minmax(0,1fr)] gap-x-2 gap-y-2 rounded-md border-2 border-edge bg-paper p-3 md:grid-cols-[2.5rem_1fr_20rem] md:items-center md:gap-3">
      <span className="tabular row-span-2 text-2xl font-extrabold text-pen md:row-span-1 md:text-3xl" aria-hidden="true">
        {rank ?? ''}
      </span>
      <div className="grid min-w-0 gap-1">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          {row.type === 'candidate' && <Portrait name={row.name} file={row.portrait} size="avatar" />}
          <h3 className="text-xl font-bold md:text-2xl">{row.name}</h3>
          {row.number && <span className="tabular text-xl font-semibold text-muted">{row.number}</span>}
        </div>
        {row.type === 'candidate' && <p className="text-base text-muted md:text-lg">{row.listName}</p>}
        {row.history && <p className="hidden text-base text-muted md:block">{row.history}</p>}
        {row.notice && <p className="rounded-sm border-2 border-contra px-3 py-2 text-base font-semibold text-contra">{row.notice}</p>}
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-base">
          <span className="text-muted">{COPY.results.coverage(row.covered, row.answered)}</span>
          {s.score !== null && <Tag strong={s.measuredShare > 0}>{row.measured}</Tag>}
        </div>
      </div>
      <div className="col-start-2 grid gap-2 md:col-start-auto">
        {s.score !== null && (
          <div className="flex items-center gap-3">
            <span className="tabular w-16 text-2xl font-extrabold md:text-3xl">{percent(s.score)}</span>
            <div className="flex-1">
              <ScoreBand score={s} />
              <p className="tabular mt-1 flex flex-wrap items-center gap-2 text-sm text-muted">
                faixa {percent(s.low)} a {percent(s.high)}
                {row.thin && <Tag strong>{COPY.results.thin}</Tag>}
              </p>
            </div>
          </div>
        )}
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="quiet" size="link" className="mr-2" onClick={() => onDetails(row)}>
            {COPY.results.details}
          </Button>
          {row.type === 'list' && onOpenList && (
            <Button size="sm" onClick={() => onOpenList(row.id)}>
              {COPY.results.chooseList}
            </Button>
          )}
          {slot ? (
            <span className="flex flex-wrap items-center gap-2">
              <span className="rounded-md bg-ink px-3 py-1.5 text-base font-bold text-paper">{COPY.results.inCola(SLOT_LABEL[slot])}</span>
              <Button variant="quiet" size="sm" onClick={() => onRemove(slot)} aria-label={`${COPY.results.remove} ${row.name} da cola`}>
                {COPY.results.remove}
              </Button>
            </span>
          ) : (
            <Button
              variant="pen"
              size="sm"
              onClick={() => onPut(row)}
              disabled={row.type === 'candidate' && slotsFull}
              title={row.type === 'candidate' && slotsFull ? COPY.results.slotsFull : undefined}
              aria-label={`${COPY.results.putInCola}: ${row.name}`}
            >
              {COPY.results.putInCola}
            </Button>
          )}
        </div>
      </div>
    </li>
  );
}
