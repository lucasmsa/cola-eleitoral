import { describe, expect, it } from 'vitest';
import { ELECTION_DAYS } from '@/config/election';
import { isElectionDay, saoPauloDate } from './electionDay';

describe('saoPauloDate', () => {
  it('reads the calendar date in America/Sao_Paulo', () => {
    expect(saoPauloDate(new Date('2026-10-04T02:59:00Z'))).toBe('2026-10-03');
    expect(saoPauloDate(new Date('2026-10-04T03:00:00Z'))).toBe('2026-10-04');
  });
});

describe('isElectionDay', () => {
  it('lists both rounds', () => {
    expect(ELECTION_DAYS).toEqual(['2026-10-04', '2026-10-25']);
  });

  it('is false until midnight in São Paulo and true from it', () => {
    expect(isElectionDay(new Date('2026-10-04T02:59:00Z'), ELECTION_DAYS)).toBe(false);
    expect(isElectionDay(new Date('2026-10-04T03:00:00Z'), ELECTION_DAYS)).toBe(true);
  });

  it('covers the whole 2nd-round day and nothing after it', () => {
    expect(isElectionDay(new Date('2026-10-26T02:59:00Z'), ELECTION_DAYS)).toBe(true);
    expect(isElectionDay(new Date('2026-10-26T03:00:00Z'), ELECTION_DAYS)).toBe(false);
  });
});
