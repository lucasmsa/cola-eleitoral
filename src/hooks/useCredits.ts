import { ELECTION_DAYS } from '@/config/election';
import { isElectionDay } from '@/lib/electionDay';

export function useCredits(now: Date = new Date()) {
  return { showCoffee: !isElectionDay(now, ELECTION_DAYS) };
}
