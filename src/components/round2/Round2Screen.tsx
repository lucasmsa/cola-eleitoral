import { COPY } from '@/config/copy';
import { useRound2 } from '@/hooks/useRound2';
import { PollPanel } from '../results/PollPanel';
import { Button, Hand, SourceLink } from '../shell/ui';
import { ComparisonRow } from './ComparisonRow';
import { Endorsements } from './Endorsements';
import { FinalistCard } from './FinalistCard';
import { Round2Cola, Round2ColaPrint } from './Round2Cola';

export function Round2Screen() {
  const r = useRound2();
  const [a, b] = r.finalists;
  return (
    <>
      <main className="screen-only mx-auto grid max-w-5xl grid-cols-[minmax(0,1fr)] gap-8 px-4 py-6 md:pl-24">
        <header className="grid gap-2">
          <Hand className="text-2xl">{COPY.round2.kicker(r.dateLabel)}</Hand>
          <h1 className="text-5xl font-extrabold leading-tight">{a && b ? COPY.round2.versus(a.name, b.name) : ''}</h1>
          <p className="max-w-[65ch] text-xl text-muted">{COPY.round2.lead}</p>
          {r.governor && <p className="max-w-[65ch] text-lg">{COPY.round2.governorDecided(r.governor.name, r.governor.pct)}</p>}
        </header>

        <section className="grid gap-4 md:grid-cols-2">
          {r.finalists.map((f) => (
            <FinalistCard key={f.id} f={f} />
          ))}
        </section>

        {r.canNudge ? (
          <section className="grid justify-items-start gap-3 rounded-md border-2 border-pen bg-pen-soft p-4">
            <p className="text-xl font-bold">{COPY.round2.nudgeTitle(r.missingCount)}</p>
            <p className="text-lg">{COPY.round2.nudgeBody}</p>
            <Button variant="pen" onClick={r.answerMissing}>
              {COPY.round2.nudgeCta}
            </Button>
          </section>
        ) : (
          <p className="text-lg text-muted">{COPY.round2.allAnswered}</p>
        )}

        <section className="grid gap-4" aria-labelledby="by-question">
          <div className="grid gap-1">
            <h2 id="by-question" className="text-3xl font-bold">
              {COPY.round2.byQuestion}
            </h2>
            <p className="text-lg text-muted">{COPY.round2.byQuestionLead}</p>
          </div>
          <ol className="grid gap-4">
            {r.rows.map((row) => (
              <ComparisonRow key={row.question.id} row={row} />
            ))}
          </ol>
        </section>

        <div className="flex flex-wrap gap-3">
          <Button onClick={r.openProfiles}>{COPY.round2.toProfiles}</Button>
          <Button variant="quiet" onClick={r.openAlignment}>
            {COPY.round2.toAlignment}
          </Button>
        </div>

        <Endorsements items={r.endorsements} />

        <PollPanel polls={r.polls2} title={COPY.round2.pollsTitle} explain={COPY.round2.pollsExplain} caption={r.pollCaption} />

        <Round2Cola />

        <p className="text-base text-muted">
          {COPY.round2.resultsSource}:{' '}
          {r.sources.map((s, i) => (
            <span key={s.url}>
              {i > 0 && ', '}
              <SourceLink label={s.label} url={s.url} />
            </span>
          ))}
        </p>
      </main>
      <Round2ColaPrint />
    </>
  );
}
