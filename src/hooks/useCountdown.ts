import { useMemo } from 'react';
import { ELECTION_DATE } from '@/config/election';
import { countdownLabel, daysUntil, toIsoDate } from '@/lib/days';

export function useCountdown(): string {
  return useMemo(() => countdownLabel(daysUntil(toIsoDate(new Date()), ELECTION_DATE)), []);
}
