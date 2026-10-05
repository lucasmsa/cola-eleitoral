import { useMemo } from 'react';
import { COPY } from '@/config/copy';
import { ELECTION_DATE } from '@/config/election';
import { round2 } from '@/data';
import { electionHeadline, toIsoDate } from '@/lib/days';
import { activeElection } from '@/lib/round2';
import { useTurnoStore } from '@/stores/turno';

export function useCountdown(): { short: string; long: string } {
  const turno = useTurnoStore((s) => s.turno);
  return useMemo(() => {
    if (turno === 1) return { short: COPY.turno.roundOneDone, long: COPY.turno.roundOneDone };
    return electionHeadline(activeElection(toIsoDate(new Date()), ELECTION_DATE, round2.date));
  }, [turno]);
}
