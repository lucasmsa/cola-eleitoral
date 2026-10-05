import { COPY } from '@/config/copy';
import { useRound2 } from '@/hooks/useRound2';
import { Portrait } from '../shell/Portrait';
import { Button, Hand } from '../shell/ui';

export function Round2Card() {
  const r = useRound2();
  const [a, b] = r.finalists;
  if (!a || !b) return null;
  return (
    <section className="grid gap-4 rounded-md border-2 border-ink bg-paper p-5 shadow-[3px_3px_0_#d7deec]" aria-labelledby="round2-card">
      <Hand className="text-2xl">{COPY.round2.kicker(r.dateLabel)}</Hand>
      <div className="flex flex-wrap items-center gap-4">
        <span className="flex items-center gap-3">
          <Portrait name={a.name} file={a.portrait} size="card" taped />
          <Portrait name={b.name} file={b.portrait} size="card" taped />
        </span>
        <h2 id="round2-card" className="min-w-0 text-4xl font-extrabold leading-tight">
          {COPY.round2.versus(a.name, b.name)}
        </h2>
      </div>
      <ul className="grid gap-1 text-lg">
        {r.finalists.map((f) => (
          <li key={f.id}>
            <b>{f.name}</b> {f.number}: {COPY.round2.firstRound(f.pctBrasil, f.pctParaiba)}
          </li>
        ))}
      </ul>
      {r.governor && <p className="text-lg text-muted">{COPY.round2.governorDecided(r.governor.name, r.governor.pct)}</p>}
      <Button variant="pen" className="justify-self-start" onClick={r.openRound2}>
        {COPY.round2.compare}
      </Button>
    </section>
  );
}
