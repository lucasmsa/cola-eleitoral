import { COPY } from '@/config/copy';
import { DataInfo } from '../shell/DataInfo';
import { useCountdown } from '@/hooks/useCountdown';
import { useHome } from '@/hooks/useHome';
import { useCover } from '@/hooks/useCover';
import { brDate } from '@/lib/text';
import { Mascot } from '../shell/Mascot';
import { RestartQuiz } from '../shell/RestartQuiz';
import { Button, Hand, ProgressBar } from '../shell/ui';
import { Cover } from './Cover';
import { Round1Card } from './Round1Card';
import { Round2Card } from './Round2Card';
import { UnitStop } from './UnitStop';

export function HomeScreen() {
  const home = useHome();
  const countdown = useCountdown();
  const cover = useCover();
  const hasCover = Boolean(cover.poster || cover.video);
  return (
    <main className="mx-auto grid max-w-3xl grid-cols-[minmax(0,1fr)] gap-10 px-4 py-8 md:pl-24">
      {home.turno === 2 ? <Round2Card /> : <Round1Card />}
      <Cover cover={cover} />
      <section className="flex flex-col items-start gap-5 sm:flex-row">
        {!hasCover && <Mascot mood="idle" size={96} />}
        <div className="grid gap-3">
          <Hand className="text-3xl">{countdown.long}</Hand>
          <h1 className="text-5xl font-extrabold leading-tight md:text-6xl">{COPY.appName}</h1>
          <p className="max-w-[60ch] text-xl text-muted">{COPY.home.lead}</p>
          <p className="text-base text-muted">{COPY.home.privacy}</p>
        </div>
      </section>

      <section className="grid gap-4" aria-labelledby="trail">
        <div className="flex items-center gap-4">
          <h2 id="trail" className="text-3xl font-bold">
            {COPY.home.trail}
          </h2>
          <span className="tabular text-lg text-muted">
            {home.answered} de {home.total}
          </span>
        </div>
        <ProgressBar value={home.total ? home.answered / home.total : 0} label="Progresso na trilha" />
        {home.allDone && (
          <div className="flex flex-wrap items-center gap-3 rounded-md border-2 border-pen bg-pen-soft p-4">
            <p className="text-xl font-semibold">{COPY.home.allDone}</p>
            <Button variant="pen" onClick={home.openResults}>
              {COPY.home.results}
            </Button>
          </div>
        )}
        <ol className="grid gap-4">
          {home.rows.map(({ unit, progress }, i) => (
            <UnitStop
              key={unit.id}
              index={i + 1}
              label={unit.label}
              blurb={unit.blurb}
              answered={progress.answered}
              total={progress.total}
              current={home.nextUnit?.id === unit.id}
              onOpen={() => home.openUnit(unit.id)}
            />
          ))}
        </ol>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <EntryCard title={COPY.home.results} hint={COPY.home.resultsHint} onOpen={home.openResults} />
        <EntryCard title={COPY.home.review} hint={COPY.home.reviewHint} onOpen={home.openReview} />
        <EntryCard title={COPY.home.cola} hint={COPY.home.colaHint} onOpen={home.openCola} />
      </section>

      {home.answered > 0 && <RestartQuiz />}
      <DataInfo>
        <p className="text-base text-muted">{COPY.footer(home.factCount, brDate(home.builtAt))}</p>
      </DataInfo>
    </main>
  );
}

function EntryCard({ title, hint, onOpen }: { title: string; hint: string; onOpen: () => void }) {
  return (
    <div className="grid content-between gap-3 rounded-md border-2 border-edge bg-paper p-4">
      <div className="grid gap-1">
        <h3 className="text-2xl font-bold">{title}</h3>
        <p className="text-lg text-muted">{hint}</p>
      </div>
      <Button onClick={onOpen}>{title}</Button>
    </div>
  );
}
