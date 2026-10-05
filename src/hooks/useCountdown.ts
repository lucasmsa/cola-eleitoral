import { useMemo } from 'react';
import { ELECTION_DATE } from '@/config/election';
import { round2 } from '@/data';
import { electionHeadline, toIsoDate } from '@/lib/days';
import { activeElection } from '@/lib/round2';

export function useCountdown(): { short: string; long: string } {
  return useMemo(() => electionHeadline(activeElection(toIsoDate(new Date()), ELECTION_DATE, round2.date)), []);
}
