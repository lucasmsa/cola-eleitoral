import { COPY } from '@/config/copy';
import { useNav } from '@/hooks/useNav';
import { answersMissing } from '@/lib/alignment';
import { Button } from '../shell/ui';

export function YouHiddenNotice({ minPerAxis, have }: { minPerAxis: number; have: { x: number; y: number } }) {
  const nav = useNav();
  const missing = answersMissing(minPerAxis, have);
  return (
    <div className="grid justify-items-start gap-3 rounded-md border-2 border-pen bg-pen-soft p-4">
      <p className="text-xl font-bold">{COPY.alignment.youHiddenTitle}</p>
      <p className="text-lg">{COPY.alignment.youHidden(missing.x, missing.y)}</p>
      <Button variant="pen" onClick={nav.goHome}>
        {COPY.alignment.keepAnswering}
      </Button>
    </div>
  );
}
