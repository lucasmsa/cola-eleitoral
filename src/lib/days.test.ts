import { describe, expect, it } from 'vitest';
import { countdownLabel, daysUntil } from './days';

describe('daysUntil', () => {
  it('counts calendar days to the election', () => {
    expect(daysUntil('2026-09-30', '2026-10-04')).toBe(4);
    expect(daysUntil('2026-10-04', '2026-10-04')).toBe(0);
    expect(daysUntil('2026-10-05', '2026-10-04')).toBe(-1);
  });

  it('labels plural, singular, today and past', () => {
    expect(countdownLabel(4)).toBe('Faltam 4 dias');
    expect(countdownLabel(1)).toBe('Falta 1 dia');
    expect(countdownLabel(0)).toBe('É hoje');
    expect(countdownLabel(-2)).toBe('O 1º turno já passou');
  });
});

describe('electionHeadline', () => {
  it('names the round and the date it counts down to', async () => {
    const { electionHeadline } = await import('./days');
    expect(electionHeadline({ round: 2, date: '2026-10-25', days: 20 })).toEqual({
      short: 'Faltam 20 dias',
      long: 'Faltam 20 dias para o 2º turno, 25 de outubro',
    });
    expect(electionHeadline({ round: 1, date: '2026-10-04', days: 0 }).long).toBe('É hoje: 1º turno, 4 de outubro');
    expect(electionHeadline({ round: 2, date: '2026-10-25', days: -1 }).short).toBe('O 2º turno já passou');
  });
});
