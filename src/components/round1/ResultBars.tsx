import { motion } from 'motion/react';
import { COPY } from '@/config/copy';
import type { BarRow } from '@/lib/round1';
import { formatInt } from '@/lib/round1';
import { titleCase } from '@/lib/text';
import { Tag } from '../shell/ui';

export function ResultBars({ rows, label }: { rows: BarRow[]; label: string }) {
  return (
    <ol className="grid gap-2" aria-label={label}>
      {rows.map((r, i) => (
        <li key={r.candidateId} className="grid gap-1">
          <div className="flex flex-wrap items-baseline justify-between gap-x-3">
            <span className={`text-lg ${r.highlight || r.elected ? 'font-bold' : ''}`}>
              {titleCase(r.ballotName)} <span className="tabular text-muted">{r.number}</span>{' '}
              <span className="text-base text-muted">{r.party}</span>
            </span>
            <span className="flex items-baseline gap-2">
              {r.elected && <Tag strong>{COPY.round1.elected}</Tag>}
              {r.status === '2º turno' && <Tag strong>{COPY.round1.runoff}</Tag>}
              <span className="tabular text-lg font-semibold">{r.pctLabel}%</span>
            </span>
          </div>
          <div className="h-3 w-full rounded-full bg-rule" aria-hidden="true">
            <motion.div
              className={`h-3 rounded-full ${r.highlight || r.elected ? 'bg-pen' : 'bg-muted'}`}
              initial={{ width: 0 }}
              animate={{ width: `${Math.max(r.width * 100, 0.5)}%` }}
              transition={{ duration: 0.5, delay: i * 0.03, ease: 'easeOut' }}
            />
          </div>
          <span className="tabular text-sm text-muted">{COPY.round1.votes(formatInt(r.votes))}</span>
        </li>
      ))}
    </ol>
  );
}
