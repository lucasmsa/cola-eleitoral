import { ELECTION_TIMEZONE } from '@/config/election';

const FORMAT = new Intl.DateTimeFormat('en-CA', { timeZone: ELECTION_TIMEZONE, year: 'numeric', month: '2-digit', day: '2-digit' });

export function saoPauloDate(now: Date): string {
  return FORMAT.format(now);
}

export function isElectionDay(now: Date, days: readonly string[]): boolean {
  return days.includes(saoPauloDate(now));
}
