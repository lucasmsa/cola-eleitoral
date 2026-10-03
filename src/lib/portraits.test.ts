import { describe, expect, it } from 'vitest';
import type { Controversy } from '@/data/schema';
import { controversiesOf } from './controversies';
import { indexPortraits, initials } from './portraits';

describe('initials', () => {
  it('takes the first and last meaningful words', () => {
    expect(initials('FLAVIO BOLSONARO')).toBe('FB');
    expect(initials('ESCRITOR AUGUSTO CURY')).toBe('AC');
    expect(initials('DR. MARCELO QUEIROGA')).toBe('MQ');
    expect(initials('LULA')).toBe('L');
    expect(initials('')).toBe('?');
  });
});

describe('indexPortraits', () => {
  it('maps candidate ids to portraits', () => {
    const p = { candidateId: 'presidente-13', file: '/portraits/presidente-13.svg', photoSource: { url: 'u', accessed: 'a', label: 'l' } };
    expect(indexPortraits([p]).get('presidente-13')).toBe(p);
  });
});

describe('controversiesOf', () => {
  it('returns one candidate items, newest first', () => {
    const c = (id: string, candidateId: string, date: string): Controversy => ({
      id,
      candidateId,
      category: 'justica',
      title: id,
      status: 'Arquivado',
      date,
      claims: [],
      response: [],
    });
    expect(controversiesOf([c('a', 'x', '2020-01-01'), c('b', 'y', '2024-01-01'), c('c', 'x', '2023-05-01')], 'x').map((i) => i.id)).toEqual(['c', 'a']);
  });
});
