import { describe, expect, it } from 'vitest';
import { cand } from '@/test/fixtures';
import { colaStatus } from './colaStatus';

describe('colaStatus', () => {
  it('warns and shows the notice when the candidate left the race', () => {
    const candidate = cand('governador-27', {
      ballotName: 'PEDRO COUTINHO',
      party: 'DC',
      notice: { text: 'Em 30/09/2026 anunciou que deixa a disputa.', sources: [] },
    });
    const s = colaStatus({ status: 'candidate', candidate }, 2);
    expect(s.kind).toBe('warn');
    expect(s.text).toContain('Pedro Coutinho, DC');
    expect(s.text).toContain('deixa a disputa');
  });

  it('confirms a regular candidate', () => {
    const s = colaStatus({ status: 'candidate', candidate: cand('senador-155', { ballotName: 'VENEZIANO', party: 'MDB' }) }, 3);
    expect(s).toEqual({ kind: 'ok', text: 'Veneziano, MDB' });
  });
});
