import type { ReactNode } from 'react';
import { COPY } from '@/config/copy';
import { useRound1 } from '@/hooks/useRound1';
import type { BarRow } from '@/lib/round1';
import { Disclosure } from '../shell/Disclosure';
import { Hand } from '../shell/ui';
import { ElectedByList } from './ElectedByList';
import { ResultBars } from './ResultBars';
import { SourceLine } from './SourceLine';
import { TurnoutPanel } from './TurnoutPanel';
import { YourVotes } from './YourVotes';

function Block({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section className="grid gap-4" aria-labelledby={id}>
      <h2 id={id} className="text-3xl font-bold">
        {title}
      </h2>
      {children}
    </section>
  );
}

const TOP = 5;

function TopAndRest({ rows, label }: { rows: BarRow[]; label: string }) {
  const rest = rows.slice(TOP);
  return (
    <>
      <ResultBars rows={rows.slice(0, TOP)} label={label} />
      {rest.length > 0 && (
        <Disclosure look="dashed" summary={<>{COPY.round1.moreCandidates(rest.length)}</>}>
          <ResultBars rows={rest} label={label} />
        </Disclosure>
      )}
    </>
  );
}

export function Round1Screen() {
  const r = useRound1();
  return (
    <main className="mx-auto grid max-w-5xl grid-cols-[minmax(0,1fr)] gap-10 px-4 py-6 md:pl-24">
      <header className="grid gap-2">
        <Hand className="text-2xl">{COPY.round1.kicker}</Hand>
        <h1 className="text-5xl font-extrabold leading-tight">{COPY.round1.title}</h1>
        <p className="max-w-[65ch] text-xl text-muted">{COPY.round1.lead}</p>
      </header>

      <YourVotes picks={r.picks} />

      <Block id="r1-presidente" title={COPY.round1.presidente}>
        <div className="grid gap-8 md:grid-cols-2">
          <div className="grid min-w-0 content-start gap-3">
            <h3 className="text-xl font-bold">{COPY.round1.brasil}</h3>
            <TopAndRest rows={r.presidenteBr} label={`${COPY.round1.presidente}, ${COPY.round1.brasil}`} />
            <SourceLine source={r.presidenteSources.br} />
          </div>
          <div className="grid min-w-0 content-start gap-3">
            <h3 className="text-xl font-bold">{COPY.round1.paraiba}</h3>
            <TopAndRest rows={r.presidentePb} label={`${COPY.round1.presidente}, ${COPY.round1.paraiba}`} />
            <SourceLine source={r.presidenteSources.pb} />
          </div>
        </div>
      </Block>

      <Block id="r1-governador" title={COPY.round1.governador}>
        <ResultBars rows={r.governador} label={COPY.round1.governador} />
        <SourceLine source={r.governadorSource} />
      </Block>

      <Block id="r1-senado" title={COPY.round1.senado}>
        <ResultBars rows={r.senador} label={COPY.round1.senado} />
        <SourceLine source={r.senadorSource} />
      </Block>

      <Block id="r1-depfed" title={COPY.round1.depFederal}>
        <p className="max-w-[65ch] text-lg text-muted">{COPY.round1.howExplain}</p>
        <Disclosure summary={<>{COPY.round1.showElected(r.depFederalTotal)}</>}>
          <ElectedByList groups={r.depFederal} total={r.depFederalTotal} portraitOf={r.portraitOf} />
        </Disclosure>
        <SourceLine source={r.depFederalSource} />
      </Block>

      <Block id="r1-depest" title={COPY.round1.depEstadual}>
        <Disclosure summary={<>{COPY.round1.showElected(r.depEstadualTotal)}</>}>
          <ElectedByList groups={r.depEstadual} total={r.depEstadualTotal} portraitOf={r.portraitOf} />
        </Disclosure>
        <SourceLine source={r.depEstadualSource} />
      </Block>

      <TurnoutPanel items={r.turnout} />
    </main>
  );
}
