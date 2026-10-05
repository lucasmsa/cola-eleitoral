import { COPY } from '@/config/copy';
import { useRound1 } from '@/hooks/useRound1';
import { titleCase } from '@/lib/text';
import { Button, Hand } from '../shell/ui';

const names = (list: { ballotName: string; pctLabel: string }[]) =>
  list.map((c) => `${titleCase(c.ballotName)} (${c.pctLabel}%)`).join(' e ');

export function Round1Card() {
  const r = useRound1();
  const { runoff, governor, senators } = r.summary;
  return (
    <section className="grid gap-3 rounded-md border-2 border-ink bg-paper p-5 shadow-[3px_3px_0_#d7deec]" aria-labelledby="round1-card">
      <Hand className="text-2xl">{COPY.round1.kicker}</Hand>
      <h2 id="round1-card" className="text-4xl font-extrabold leading-tight">
        {COPY.round1.title}
      </h2>
      <ul className="grid gap-1 text-lg">
        {runoff.length > 0 && <li>{COPY.round1.runoffLine(names(runoff))}</li>}
        {governor && <li>{COPY.round1.governorLine(titleCase(governor.ballotName), governor.pctLabel)}</li>}
        {senators.length > 0 && <li>{COPY.round1.senatorsLine(names(senators))}</li>}
      </ul>
      <Button variant="pen" className="justify-self-start" onClick={r.openRound1}>
        {COPY.round1.card}
      </Button>
    </section>
  );
}
