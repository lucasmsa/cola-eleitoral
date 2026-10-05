import { COPY } from '@/config/copy';
import type { FinalistView } from '@/hooks/useRound2';
import { percent } from '@/lib/text';
import { ScoreBand } from '../results/ScoreBand';
import { Portrait } from '../shell/Portrait';
import { Tag } from '../shell/ui';

export function FinalistCard({ f }: { f: FinalistView }) {
  return (
    <article className="grid min-w-0 content-start gap-3 rounded-md border-2 border-edge bg-paper p-4" data-testid={`finalist-${f.number}`}>
      <div className="flex items-start gap-4">
        <Portrait name={f.name} file={f.portrait} size="card" taped />
        <div className="grid min-w-0 gap-1">
          <h3 className="text-3xl font-extrabold leading-tight">
            {f.name} <span className="tabular text-muted">{f.number}</span>
          </h3>
          <p className="text-base text-muted">{COPY.round2.firstRound(f.pctBrasil, f.pctParaiba)}</p>
        </div>
      </div>
      {f.score.score === null ? (
        <p className="text-lg text-muted">{COPY.round2.noScore}</p>
      ) : (
        <div className="grid gap-2">
          <p className="flex items-baseline gap-2">
            <span className="tabular text-4xl font-extrabold">{percent(f.score.score)}</span>
            <span className="text-lg text-muted">{COPY.round2.agree}</span>
          </p>
          <ScoreBand score={f.score} />
          <p className="tabular text-sm text-muted">
            faixa {percent(f.score.low)} a {percent(f.score.high)}
          </p>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2 text-base">
        <span className="text-muted">{f.coverage}</span>
        {f.score.score !== null && <Tag strong={f.score.measuredShare > 0}>{f.measured}</Tag>}
      </div>
    </article>
  );
}
