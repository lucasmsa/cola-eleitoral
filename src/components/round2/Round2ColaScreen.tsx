import { COPY } from '@/config/copy';
import { useRound2 } from '@/hooks/useRound2';
import { Hand } from '../shell/ui';
import { Round2Cola, Round2ColaPrint } from './Round2Cola';

export function Round2ColaScreen() {
  const r = useRound2();
  return (
    <>
      <main className="screen-only mx-auto grid max-w-5xl grid-cols-[minmax(0,1fr)] gap-6 px-4 py-6 md:pl-24">
        <Hand className="text-2xl">{COPY.round2.kicker(r.dateLabel)}</Hand>
        <Round2Cola />
      </main>
      <Round2ColaPrint />
    </>
  );
}
