import { COPY } from '@/config/copy';
import type { Evidence } from '@/data/schema';
import { POSITION_LABEL, positionTone } from '@/lib/positions';
import { evidenceBadge } from '@/lib/subjects';
import { brDate } from '@/lib/text';
import { SourceLink, Tag, ToneChip } from '../shell/ui';

export function EvidenceLine({ evidence, statement }: { evidence: Evidence; statement?: string }) {
  const tone = positionTone(evidence.position);
  return (
    <li className="grid gap-2 border-l-2 border-rule pl-3">
      {statement && <p className="text-lg font-semibold">{statement}</p>}
      <div className="flex flex-wrap items-center gap-2">
        <ToneChip tone={tone}>{POSITION_LABEL[tone]}</ToneChip>
        <Tag strong={evidence.kind === 'record'}>{evidenceBadge(evidence)}</Tag>
        <span className="tabular text-base text-muted">{brDate(evidence.date)}</span>
      </div>
      <p className="text-lg">{evidence.detail}</p>
      {evidence.quote && <blockquote className="border-l-4 border-pen pl-3 text-lg text-ink">“{evidence.quote}”</blockquote>}
      {evidence.lowDiscrimination && <p className="font-hand text-xl text-pen">{COPY.fact.lowDiscrimination}</p>}
      <p className="text-base break-words text-muted">
        {COPY.fact.source}: <SourceLink label={evidence.source.label} url={evidence.source.url} />
      </p>
    </li>
  );
}
