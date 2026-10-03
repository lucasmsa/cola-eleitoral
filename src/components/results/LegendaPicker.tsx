import { COPY } from '@/config/copy';
import { Button } from '../shell/ui';

interface Props {
  listName: string;
  parties: { number: string; party: string }[];
  onPick: (number: string) => void;
  onCancel: () => void;
}

export function LegendaPicker({ listName, parties, onPick, onCancel }: Props) {
  return (
    <div className="fixed inset-0 z-30 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-labelledby="legenda-title">
      <div className="grid w-full max-w-lg gap-4 rounded-md border-2 border-ink bg-paper p-5">
        <h2 id="legenda-title" className="text-3xl font-bold">
          {COPY.results.legendaTitle(listName)}
        </h2>
        <p className="text-lg text-muted">{COPY.results.legendaExplain}</p>
        <div className="flex flex-wrap gap-2">
          {parties.map((p) => (
            <Button key={p.number} variant="pen" onClick={() => onPick(p.number)}>
              {p.number} ({p.party})
            </Button>
          ))}
        </div>
        <div>
          <Button variant="quiet" onClick={onCancel}>
            {COPY.results.cancel}
          </Button>
        </div>
      </div>
    </div>
  );
}
